from django.shortcuts import render
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from home import models as HomeModels
from .forms import GymMembershipForm

class DashBoardView(TemplateView):
    template_name = "GodMode/dashboard.html"

class ContactListView(ListView):
    model = HomeModels.ContactMessage
    template_name = "GodMode/contacts.html"
    context_object_name = "contacts"

# gym membership
class GymMembershipListView(ListView):
    model = HomeModels.GymMembership
    template_name = 'GodMode/list.html'
    context_object_name = 'memberships'


class GymMembershipCreateView(CreateView):
    model = HomeModels.GymMembership
    form_class = GymMembershipForm
    template_name = 'GodMode/form.html'
    success_url = reverse_lazy('godmode:membership_list')


class GymMembershipUpdateView(UpdateView):
    model = HomeModels.GymMembership
    form_class = GymMembershipForm
    template_name = 'GodMode/form.html'
    success_url = reverse_lazy('godmode:membership_list')


class GymMembershipDeleteView(DeleteView):
    model = HomeModels.GymMembership
    success_url = reverse_lazy('godmode:membership_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

# finance management
from .models import Expense, Income
from .forms import ExpenseForm, IncomeForm
# expense
class ExpenseListView(ListView):
    model = Expense
    template_name = "GodMode/expenses.html"
    context_object_name = "expenses"

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'GodMode/expense_form.html'
    success_url = reverse_lazy('godmode:expenses')

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'GodMode/expense_form.html'
    success_url = reverse_lazy('godmode:expenses')


class ExpenseDeleteView(DeleteView):
    model = Expense
    success_url = reverse_lazy('godmode:expenses')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

# income
# income
class IncomeListView(ListView):
    model = Income
    template_name = "GodMode/incomes.html"
    context_object_name = "incomes"


class IncomeCreateView(CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'GodMode/income_form.html'
    success_url = reverse_lazy('godmode:incomes')


class IncomeUpdateView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'GodMode/income_form.html'
    success_url = reverse_lazy('godmode:incomes')


class IncomeDeleteView(DeleteView):
    model = Income
    success_url = reverse_lazy('godmode:incomes')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


# check in
from .models import DailyCheckIn
from .forms import DailyCheckInForm

class CheckInListView(ListView):
    model = DailyCheckIn
    template_name = "GodMode/checkins.html"
    context_object_name = "checkins"


# CREATE
class CheckInCreateView(CreateView):
    model = DailyCheckIn
    form_class = DailyCheckInForm
    template_name = "GodMode/checkin_form.html"
    success_url = reverse_lazy('godmode:checkins')


# UPDATE
class CheckInUpdateView(UpdateView):
    model = DailyCheckIn
    form_class = DailyCheckInForm
    template_name = "GodMode/checkin_form.html"
    success_url = reverse_lazy('godmode:checkins')


# DELETE
class CheckInDeleteView(DeleteView):
    model = DailyCheckIn
    success_url = reverse_lazy('godmode:checkins')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)