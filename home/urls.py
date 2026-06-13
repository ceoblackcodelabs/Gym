from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),

    # API Endpoints
    path('api/contact/', views.ContactAPIView.as_view(), name='api_contact'),
    path('api/register-membership/', views.MembershipRegistrationAPIView.as_view(), name='api_register_membership'),
    path('api/check-user/', views.CheckMemberExistsAPIView.as_view(), name='api_check_user'),
]