from django.shortcuts import render
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from home import models as HomeModels
from home.models import GymMembership
from django.db.models import Sum
from .forms import GymMembershipForm
from datetime import timedelta
import json
import calendar
from django.utils import timezone

class DashBoardView(TemplateView):
    template_name = "GodMode/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # =========================
        # Dashboard Cards
        # =========================

        total_income = Income.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_expenses = Expense.objects.aggregate(
            total=Sum('price')
        )['total'] or 0

        context['dashboard'] = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': total_income - total_expenses,

            'active_members': GymMembership.objects.filter(
                status='active'
            ).count(),

            'today_checkins': DailyCheckIn.objects.filter(
                checkin_date=timezone.now().date()
            ).count(),

            'inventory_items': Inventory.objects.count(),

            'faulty_inventory': Inventory.objects.filter(
                condition='faulty'
            ).count(),
        }

        # =========================
        # Monthly Income vs Expenses
        # =========================

        income_expense_labels = []
        income_data = []
        expense_data = []

        current_year = timezone.now().year

        for month in range(1, 13):

            income_total = Income.objects.filter(
                date_received__month=month,
                date_received__year=current_year
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            expense_total = Expense.objects.filter(
                date__month=month,
                date__year=current_year
            ).aggregate(
                total=Sum('price')
            )['total'] or 0

            income_expense_labels.append(
                calendar.month_abbr[month]
            )

            income_data.append(float(income_total))
            expense_data.append(float(expense_total))

        context['income_expense_labels'] = json.dumps(
            income_expense_labels
        )

        context['income_data'] = json.dumps(
            income_data
        )

        context['expense_data'] = json.dumps(
            expense_data
        )

        # =========================
        # Daily Checkins (Last 30 Days)
        # =========================

        checkin_labels = []
        checkin_data = []

        for i in range(29, -1, -1):

            day = timezone.now().date() - timedelta(days=i)

            total = DailyCheckIn.objects.filter(
                checkin_date=day
            ).count()

            checkin_labels.append(
                day.strftime('%d %b')
            )

            checkin_data.append(total)

        context['checkin_labels'] = json.dumps(
            checkin_labels
        )

        context['checkin_data'] = json.dumps(
            checkin_data
        )

        # =========================
        # Inventory Condition
        # =========================

        context['inventory_condition_labels'] = json.dumps([
            'Good',
            'Faulty',
            'Maintenance'
        ])

        context['inventory_condition_data'] = json.dumps([
            Inventory.objects.filter(
                condition='good'
            ).count(),

            Inventory.objects.filter(
                condition='faulty'
            ).count(),

            Inventory.objects.filter(
                condition='maintenance'
            ).count(),
        ])

        # =========================
        # Recent Checkins
        # =========================

        context['recent_checkins'] = DailyCheckIn.objects.select_related(
            'member',
            'member__user'
        ).order_by(
            '-checkin_time'
        )[:10]

        # =========================
        # Recent Income
        # =========================

        context['recent_income'] = Income.objects.order_by(
            '-date_received'
        )[:5]

        # =========================
        # Recent Expenses
        # =========================

        context['recent_expenses'] = Expense.objects.order_by(
            '-date'
        )[:5]

        # =========================
        # Membership Breakdown
        # =========================

        context['membership_labels'] = json.dumps([
            'Rookie',
            'Warrior',
            'Elite'
        ])

        context['membership_data'] = json.dumps([
            GymMembership.objects.filter(
                membership_plan='rookie'
            ).count(),

            GymMembership.objects.filter(
                membership_plan='warrior'
            ).count(),

            GymMembership.objects.filter(
                membership_plan='elite'
            ).count(),
        ])

        return context

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

# inventory
from .models import Inventory
from .forms import InventoryForm
class InventoryListView(ListView):
    model = Inventory
    template_name = "GodMode/inventory.html"
    context_object_name = "inventory"


class InventoryCreateView(CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "GodMode/inventory_form.html"
    success_url = reverse_lazy('godmode:inventory')


class InventoryUpdateView(UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "GodMode/inventory_form.html"
    success_url = reverse_lazy('godmode:inventory')


class InventoryDeleteView(DeleteView):
    model = Inventory
    success_url = reverse_lazy('godmode:inventory')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)