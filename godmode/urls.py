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

    # finance
    path('expenses/', ExpenseListView.as_view(), name="expenses"),
    path('expenses/create/', ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/update/<int:pk>/', ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense_delete'),
]
