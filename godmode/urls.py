from django.urls import path
from .views import *

app_name = "godmode"

urlpatterns = [
    path("", DashBoardView.as_view(), name="dashboard"),
    path("contacts/", ContactListView.as_view(), name="contact"),

    # membership
    path('membership/', GymMembershipListView.as_view(), name='membership_list'),
    path('create/', GymMembershipCreateView.as_view(), name='membership_create'),
    path('<int:pk>/edit/', GymMembershipUpdateView.as_view(), name='membership_update'),
    path('<int:pk>/delete/', GymMembershipDeleteView.as_view(), name='membership_delete'),
]
