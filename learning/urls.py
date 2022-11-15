from django.views.decorators.cache import cache_control, never_cache
from django.urls import path
from .views import *


urlpatterns = [
    path('', MainView.as_view(), name='index'),
    path('create/', CourseCreateView.as_view(), name='create'),
    path('detail/<int:course_id>/', cache_control(max_age=600)(CourseDetailView.as_view()), name='detail'),
    path('update/<int:course_id>/', CourseUpdateView.as_view(), name='update'),
    path('delete/<int:course_id>/', CourseDeleteView.as_view(), name='delete'),
    path('enroll/<int:course_id>/', enroll, name='enroll'),
    path('review/<int:course_id>/', review, name='review'),
    path('<int:course_id>/create_lesson/', LessonCreateView.as_view(), name='create_lesson'),
    # paths for session work
    path('add_booking/<int:course_id>/', add_booking, name='add_booking'),
    path('remove_booking/<int:course_id>/', remove_booking, name='remove_booking'),
    path('favourites/', never_cache(FavouriteView.as_view()), name='favourites'),
    path('settings/', SettingFormView.as_view(), name='settings'),

    path('get_certificate/<int:course_id>/', get_certificate_view, name='get_certificate'),
    path('tracking/', TrackingView.as_view(), name='tracking'),
]
