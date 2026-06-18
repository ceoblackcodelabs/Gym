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

    # income
    path('incomes/', IncomeListView.as_view(), name='incomes'),
    path('income/create/', IncomeCreateView.as_view(), name='income_create'),
    path('income/<int:pk>/update/', IncomeUpdateView.as_view(), name='income_update'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='income_delete'),

    # check in
    path('checkins/', CheckInListView.as_view(), name='checkins'),
    path('checkin/create/', CheckInCreateView.as_view(), name='checkin_create'),
    path('checkin/<int:pk>/update/', CheckInUpdateView.as_view(), name='checkin_update'),
    path('checkin/<int:pk>/delete/', CheckInDeleteView.as_view(), name='checkin_delete'),

    # inventory
    path('inventory/', InventoryListView.as_view(), name='inventory'),
    path('inventory/create/', InventoryCreateView.as_view(), name='inventory_create'),
    path('inventory/<int:pk>/update/', InventoryUpdateView.as_view(), name='inventory_update'),
    path('inventory/<int:pk>/delete/', InventoryDeleteView.as_view(), name='inventory_delete'),

    # qrs
    path("qrs/", QRCheckinView.as_view(), name="qrs_checkin"),

    # Membership Detail with QR
    path('membership/<int:pk>/', MembershipDetailView.as_view(), name='membership_detail'),

    # Membership Delete
    path('membership/<int:pk>/delete/', MembershipDeleteView.as_view(), name='membership_delete'),

    # QR Code only view
    path('membership/<int:pk>/qr/', MembershipQRView.as_view(), name='membership_qr'),

    # Check-in endpoint (called when QR is scanned)
    path('checkin/<int:membership_id>/<int:user_id>/', MemberCheckinView.as_view(), name='member_checkin'),
]
