from django.contrib.auth.views import (LogoutView, PasswordResetView,
                                       PasswordResetDoneView, PasswordResetConfirmView,
                                       PasswordResetCompleteView, PasswordChangeView,
                                       PasswordChangeDoneView)
from django.views.decorators.cache import cache_control
from django.urls import path
from .views import *


urlpatterns = [
    path('login/', cache_control(private=True)(UserLoginView.as_view()), name='login'),
    path('register/', cache_control(private=True)(RegisterView.as_view()), name='register'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),

    # Обработчики для смены пароля
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Обработчики для сброса пароля
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
