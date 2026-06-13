from django.urls import path
from .views import *

urlpatterns = [
    path("", DashBoardView.as_view(), name="dashboard")
]
