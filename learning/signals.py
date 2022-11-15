from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection, EmailMessage
from django.db.models.signals import pre_save, post_save
from django.dispatch import Signal, receiver
from django.template.loader import render_to_string
from .models import Course, Lesson

set_views = Signal()
course_enroll = Signal()
get_certificate = Signal()


def check_quantity(sender, instance, **kwargs):
    error = None
    actual_count = sender.objects.filter(course=instance.course).count()
    set_count = Course.objects.filter(id=instance.course.id).values('count_lessons')[0]['count_lessons']

    if actual_count >= set_count:
        error = f'Количество уроков ограничено! ' \
                f'Ранее вы установили, что курс будет содержать {set_count} уроков'

    return error


def incr_views(**kwargs):
    session = kwargs['session']
    views = session.setdefault('views', {})
    course_id = str(kwargs['id'])
    count = views.get(course_id, 0)
    views[course_id] = count + 1
    session['views'] = views
    session.modified = True


def send_enroll_email(**kwargs):
    template_name = 'emails/course_info_email.html'
    course = Course.objects.get(id=kwargs['course_id'])
    context = {
        'course': course,
        'message': f'Вы были успешно записаны на курс {course.title}.'
                   f'Первый урок будет доступен уже {course.start_date}. Не пропустите!'
    }
    send_mail(subject='Запись на курс | Платформа Codeby',
              message='',
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[kwargs['request'].user.email],
              html_message=render_to_string(template_name, context, kwargs['request']),
              fail_silently=False)


def send_user_certificate(**kwargs):
    template_name = 'emails/certificate_email.html'
    context = {
        'message': 'Поздравляем! Вы успешно закончили курс.'
                   '\nВо вложении прилагаем сертификат о прохождении'
    }
    email = EmailMultiAlternatives(subject='Сертификат о прохождении курса | Платформа Codeby',
                                   to=[kwargs['sender'].email])
    email.attach_alternative(render_to_string(template_name, context), mimetype='text/html')
    email.attach_file(path=settings.MEDIA_ROOT / 'certificates/certificate.png', mimetype='image/png')
    email.send(fail_silently=True)


@receiver(post_save, sender=Lesson)
def send_info_email(sender, instance, **kwargs):
    if kwargs['created']:
        actual_count = sender.objects.filter(course=instance.course).count()
        set_count = Course.objects.filter(id=instance.course.id).values('count_lessons')[0]['count_lessons']

        if actual_count == set_count:
            template_name = 'emails/course_info_email.html'
            course = Course.objects.get(id=instance.course.id)
            context = {
                'course': course,
                'message': f'На нешей платформе появился новый курс {course.title}.'
                           f'\nПодробную информацию Вы можете получить по ссылке ниже'
            }
            user = get_user_model()
            recipients = user.objects.exclude(is_staff=True).values_list('email', flat=True)

            connection = get_connection(fail_silently=True)
            connection.open()

            EmailMessage.content_subtype = 'html'
            emails = [
                EmailMessage(subject='Время обучиться новому скиллу | Платформа Codeby',
                             body=render_to_string(template_name, context),
                             to=[email], connection=connection)
                for email in recipients
            ]

            connection.send_messages(emails)
            connection.close()


pre_save.connect(check_quantity, sender=Lesson)
set_views.connect(incr_views)
course_enroll.connect(send_enroll_email)
get_certificate.connect(send_user_certificate)
