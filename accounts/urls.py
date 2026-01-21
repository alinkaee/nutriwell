from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_client_profile, name='edit_client_profile'),
    path('nutrition-plan/', views.nutrition_plan, name='nutrition_plan'),
    path('clients/', views.nutritionist_clients, name='nutritionist_clients'),
    path('programs/', views.nutritionist_programs, name='nutritionist_programs'),
    path('analytics/', views.nutritionist_analytics, name='nutritionist_analytics'),
    path('clients/assign/<int:client_id>/', views.assign_client, name='assign_client'),
    path('invite-client/', views.invite_client, name='invite_client'),
    path('accept-invitation/<int:notification_id>/', views.accept_invitation, name='accept_invitation'),
    path('dismiss-invitation/<int:notification_id>/', views.dismiss_invitation, name='dismiss_invitation'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
