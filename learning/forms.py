from .models import Course, Review, Lesson
from django import forms
from django.forms.widgets import Textarea, TextInput
from django.forms.utils import ValidationError


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ('title', 'description', 'start_date', 'duration', 'price', 'count_lessons')


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ('content', )


class LessonForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label='Выберите курс', required=True,
                                    label='Курс', help_text='Укажите курс, к которому Вы хотите добавить урок!')
    preview = forms.CharField(widget=Textarea(attrs={
        'placeholder': 'Опишите содержание урока',
        'rows': 20,
        'cols': 35,
    }), label='')

    error_css_class = 'error_field'
    required_css_class = 'required_field'

    class Meta:
        model = Lesson
        fields = ('name', 'preview', 'course', )

    def clean_preview(self):
        preview_data = self.cleaned_data['preview']
        if len(preview_data) > 200:
            raise ValidationError('Слишком длинное описание! Сократите до 200 символов')
        return preview_data


class OrderByAndSearchForm(forms.Form):

    PRICE_CHOICES = (
        ('title', 'По умолчанию'),
        ('price', 'Самые дешёвые курсы'),
        ('-price', 'Самые дорогие курсы'),
    )

    search = forms.CharField(label='Поиск', label_suffix=':', required=False,
                             widget=TextInput(attrs={'placeholder': 'Введите запрос ...'}))
    price_order = forms.ChoiceField(label='', choices=PRICE_CHOICES, initial=PRICE_CHOICES[0])


class SettingForm(forms.Form):
    paginate_by = forms.IntegerField(label='Записей на одной странице', min_value=2, max_value=20, initial=5)
