from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import transaction
from django.db.models import Q, F, Sum, Count
from django.db.models.signals import pre_save
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from datetime import datetime
from .models import Course, Lesson, Tracking, Review
from .forms import CourseForm, ReviewForm, LessonForm, OrderByAndSearchForm, SettingForm
from .signals import set_views, course_enroll, get_certificate


class MainView(ListView, FormView):
    template_name = 'index.html'
    queryset = Course.objects.all()
    context_object_name = 'courses'

    form_class = OrderByAndSearchForm

    def get_queryset(self):
        if 'courses' in cache:
            queryset = cache.get('courses')
        else:
            queryset = MainView.queryset
            cache.set('courses', queryset, timeout=30)

        if {'search', 'price_order'} != self.request.GET.keys():
            return queryset
        else:
            search_query = self.request.GET.get('search')
            price_order_by = self.request.GET.get('price_order')
            filter = Q(title__icontains=search_query) | Q(description__icontains=search_query)
            queryset = queryset.filter(filter).order_by(price_order_by)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        return context

    def get_initial(self):
        initial = super(MainView, self).get_initial()
        initial['search'] = self.request.GET.get('search', '')
        initial['price_order'] = self.request.GET.get('price_order', 'title')
        return initial

    def get_paginate_by(self, queryset):
        return self.request.COOKIES.get('paginate_by', 5)


class CourseDetailView(ListView):
    template_name = 'detail.html'
    context_object_name = 'lessons'
    pk_url_kwarg = 'course_id'
    
    def get(self, request, *args, **kwargs):
        set_views.send(sender=self.__class__,
                       session=request.session,
                       pk_url_kwarg=CourseDetailView.pk_url_kwarg,
                       id=kwargs[CourseDetailView.pk_url_kwarg])

        return super(CourseDetailView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        queryset = cache.get_or_set(f'course_{course_id}_lessons',
                                    Lesson.objects.select_related('course').filter(course=course_id),
                                    timeout=30)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['reviews'] = Review.objects.select_related('user').filter(course=self.kwargs.get('course_id'))
        return context


class CourseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'create.html'

    permission_required = ('learning.add_course', )

    def form_valid(self, form):
        with transaction.atomic():
            course = form.save(commit=False)
            course.save()
            course.authors.add(self.request.user)
            cache.delete('courses')
            return redirect(reverse('create_lesson', kwargs={'course_id': course.id}))


class CourseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'create.html'
    pk_url_kwarg = 'course_id'

    permission_required = ('learning.change_course', )

    def get_queryset(self):
        return Course.objects.filter(id=self.kwargs.get('course_id'))

    def get_success_url(self):
        return reverse('detail', kwargs={'course_id': self.object.id})


class CourseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'delete.html'
    pk_url_kwarg = 'course_id'

    permission_required = ('learning.delete_course', )
    
    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        cache.delete_many(['courses', f"course_{course_id}_lessons"])
        return super(CourseDeleteView, self).form_valid(form)

    def get_queryset(self):
        return Course.objects.filter(id=self.kwargs.get('course_id'))

    def get_success_url(self):
        return reverse('index')


class LessonCreateView(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Lesson
    form_class = LessonForm
    template_name = 'create_lesson.html'
    pk_url_kwarg = 'course_id'

    permission_required = ('learning.add_lesson',)
    
    def form_valid(self, form):
        error = pre_save.send(sender=LessonCreateView.model, instance=form.save(commit=False))
        if error[0][1]:
            form.errors[NON_FIELD_ERRORS] = [error[0][1]]
            return super(LessonCreateView, self).form_invalid(form)
        else:
            return super(LessonCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('detail', kwargs={'course_id': self.kwargs.get('course_id')})

    def get_form(self, form_class=None):
        form = super(LessonCreateView, self).get_form()
        form.fields['course'].queryset = Course.objects.filter(authors=self.request.user)
        return form


class FavouriteView(MainView):

    def get_queryset(self):
        queryset = super(FavouriteView, self).get_queryset()
        ids = self.request.session.get('favourites', list())
        return queryset.filter(id__in=ids)


class SettingFormView(FormView):
    form_class = SettingForm
    template_name = 'settings.html'

    def post(self, request, *args, **kwargs):
        paginate_by = request.POST.get('paginate_by')
        print(request.POST)
        response = HttpResponseRedirect(reverse('index'), 'Настройки успешно сохранены!')
        response.set_cookie('paginate_by', value=paginate_by, secure=False,
                            httponly=False, samesite='Lax', max_age=60 * 60 * 24 * 365)
        return response

    def get_initial(self):
        initial = super(SettingFormView, self).get_initial()
        initial['paginate_by'] = self.request.COOKIES.get('paginate_by', 5)
        return initial


class TrackingView(LoginRequiredMixin, ListView):
    model = Tracking
    template_name = 'tracking.html'
    context_object_name = 'tracks'

    def get_queryset(self):
        queryset = Tracking.objects\
            .select_related('lesson')\
            .filter(user=self.request.user)\
            .annotate(header=F('lesson__course__title'))
        return queryset


@transaction.atomic
@login_required
@permission_required('learning.add_tracking', raise_exception=True)
def enroll(request, course_id):
    is_existed = Tracking.objects.filter(user=request.user, lesson__course=course_id).exists()
    if is_existed:
        return HttpResponse(f'Вы уже записаны на данный курс')
    else:
        lessons = Lesson.objects.filter(course=course_id)
        records = [Tracking(lesson=lesson, user=request.user, passed=False) for lesson in lessons]
        Tracking.objects.bulk_create(records)

        # Отправка письма об успешной записи на курс
        course_enroll.send(sender=Tracking, request=request, course_id=course_id)

        return redirect('tracking')


@transaction.non_atomic_requests
@login_required
@permission_required('learning.add_review', raise_exception=True)
def review(request, course_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.errors:
            errors = form.errors[NON_FIELD_ERRORS]
            return render(request, 'review.html', {'form': form, 'errors': errors})
        if form.is_valid():
            data = form.cleaned_data
            Review.objects.create(content=data['content'],
                                  course=Course.objects.get(id=course_id),
                                  user=request.user)
        return redirect(reverse('detail', kwargs={'course_id': course_id}))
    else:
        form = ReviewForm()
        return render(request, 'review.html', {'form': form})


def add_booking(request, course_id):
    if request.method == 'POST':
        favourites = request.session.get('favourites', list())
        favourites.append(course_id)
        request.session['favourites'] = favourites
        request.session.modified = True

    return redirect(reverse('index'))


def remove_booking(request, course_id):
    if request.method == 'POST':
        request.session.get('favourites').remove(course_id)
        request.session.modified = True

    return redirect(reverse('index'))


@login_required
def get_certificate_view(request, course_id):
    count_passed = Tracking.objects.filter(lesson__course=course_id, user=request.user)\
        .aggregate(total_passed=Count('lesson__course'), fact_passed=Sum('passed'))

    if count_passed['total_passed'] == count_passed['fact_passed']:
        get_certificate.send(sender=request.user)
        return HttpResponse('Сертификат отправлен на Ваш email')
    else:
        return HttpResponse('Вы не прошли полностью курс')
