from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile Management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/me/', views.user_profile_view, name='profile_me'),
    
    # Email Verification
    path('verify-email/', views.email_verification_view, name='verify_email'),
    path('verification-status/', views.check_verification_status, name='verification_status'),
]