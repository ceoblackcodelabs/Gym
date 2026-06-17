from django.shortcuts import render
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from home import models as HomeModels
from home.models import GymMembership, ContactMessage
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

        for i in range(6, -1, -1):

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
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard stats
        total_contacts = ContactMessage.objects.count()
        unread_contacts = ContactMessage.objects.filter(is_read=False).count()
        read_contacts = ContactMessage.objects.filter(is_read=True).count()

        # Today's messages
        today = timezone.now().date()
        today_contacts = ContactMessage.objects.filter(
            created_at__date=today
        ).count()

        # Response rate (if there are messages, calculate percentage read)
        if total_contacts > 0:
            response_rate = round((read_contacts / total_contacts) * 100, 1)
        else:
            response_rate = 0

        context['dashboard'] = {
            'total_contacts': total_contacts,
            'unread_contacts': unread_contacts,
            'read_contacts': read_contacts,
            'today_contacts': today_contacts,
            'response_rate': response_rate,
        }

        # Recent contacts for sidebar
        context['recent_contacts'] = ContactMessage.objects.order_by('-created_at')[:5]

        return context

# gym membership
class GymMembershipListView(ListView):
    model = HomeModels.GymMembership
    template_name = 'GodMode/membership_list.html'
    context_object_name = 'memberships'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Monthly membership data for the last 12 months
        membership_labels = []
        active_data = []
        inactive_data = []

        current_year = timezone.now().year

        for month in range(1, 13):
            month_start = timezone.datetime(current_year, month, 1)
            if month == 12:
                month_end = timezone.datetime(current_year + 1, 1, 1)
            else:
                month_end = timezone.datetime(current_year, month + 1, 1)

            # Count active members for this month
            active_count = GymMembership.objects.filter(
                status='active',
                start_date__lte=month_end,
                end_date__gte=month_start
            ).count()

            # Count inactive members (cancelled or expired)
            inactive_count = GymMembership.objects.filter(
                status__in=['cancelled', 'expired'],
                end_date__gte=month_start,
                end_date__lte=month_end
            ).count()

            membership_labels.append(calendar.month_abbr[month])
            active_data.append(active_count)
            inactive_data.append(inactive_count)

        context['membership_labels'] = json.dumps(membership_labels)
        context['active_data'] = json.dumps(active_data)
        context['inactive_data'] = json.dumps(inactive_data)

        # Membership plan distribution
        plan_labels = ['Rookie', 'Warrior', 'Elite']
        plan_data = [
            GymMembership.objects.filter(membership_plan='rookie').count(),
            GymMembership.objects.filter(membership_plan='warrior').count(),
            GymMembership.objects.filter(membership_plan='elite').count()
        ]

        context['plan_labels'] = json.dumps(plan_labels)
        context['plan_data'] = json.dumps(plan_data)

        # Dashboard summary data
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0

        context['dashboard'] = {
            'cash_at_hand': total_expenses,  # Adjust based on your logic
            'cash_at_bank': total_income,    # Adjust based on your logic
            'expenses': total_expenses,
            'total_sales': total_income,
        }

        return context

class GymMembershipCreateView(CreateView):
    model = HomeModels.GymMembership
    form_class = GymMembershipForm
    template_name = 'GodMode/membersip_form.html'
    success_url = reverse_lazy('godmode:membership_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Plan distribution data
        plan_labels = ['Rookie', 'Warrior', 'Elite']
        plan_data = [
            GymMembership.objects.filter(membership_plan='rookie').count(),
            GymMembership.objects.filter(membership_plan='warrior').count(),
            GymMembership.objects.filter(membership_plan='elite').count()
        ]

        context['plan_labels'] = json.dumps(plan_labels)
        context['plan_data'] = json.dumps(plan_data)

        # Dashboard stats
        total_members = GymMembership.objects.count()
        active_members = GymMembership.objects.filter(status='active').count()
        pending_members = GymMembership.objects.filter(status='pending').count()
        expired_members = GymMembership.objects.filter(status='expired').count()

        # Expiring soon (within 7 days)
        from django.utils import timezone
        from datetime import timedelta

        expiring_soon = GymMembership.objects.filter(
            status='active',
            end_date__lte=timezone.now() + timedelta(days=7),
            end_date__gte=timezone.now()
        ).count()

        # Active rate
        if total_members > 0:
            active_rate = round((active_members / total_members) * 100, 1)
        else:
            active_rate = 0

        context['dashboard'] = {
            'total_members': total_members,
            'active_members': active_members,
            'pending_members': pending_members,
            'expired_members': expired_members,
            'active_rate': active_rate,
            'expiring_soon': expiring_soon,
            'rookie_count': GymMembership.objects.filter(membership_plan='rookie').count(),
            'warrior_count': GymMembership.objects.filter(membership_plan='warrior').count(),
            'elite_count': GymMembership.objects.filter(membership_plan='elite').count(),
        }

        return context


class GymMembershipUpdateView(UpdateView):
    model = HomeModels.GymMembership
    form_class = GymMembershipForm
    template_name = 'GodMode/membersip_form.html'
    success_url = reverse_lazy('godmode:membership_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Plan distribution data
        plan_labels = ['Rookie', 'Warrior', 'Elite']
        plan_data = [
            GymMembership.objects.filter(membership_plan='rookie').count(),
            GymMembership.objects.filter(membership_plan='warrior').count(),
            GymMembership.objects.filter(membership_plan='elite').count()
        ]

        context['plan_labels'] = json.dumps(plan_labels)
        context['plan_data'] = json.dumps(plan_data)

        # Dashboard stats
        total_members = GymMembership.objects.count()
        active_members = GymMembership.objects.filter(status='active').count()
        pending_members = GymMembership.objects.filter(status='pending').count()
        expired_members = GymMembership.objects.filter(status='expired').count()

        # Expiring soon (within 7 days)
        from django.utils import timezone
        from datetime import timedelta

        expiring_soon = GymMembership.objects.filter(
            status='active',
            end_date__lte=timezone.now() + timedelta(days=7),
            end_date__gte=timezone.now()
        ).count()

        # Active rate
        if total_members > 0:
            active_rate = round((active_members / total_members) * 100, 1)
        else:
            active_rate = 0

        context['dashboard'] = {
            'total_members': total_members,
            'active_members': active_members,
            'pending_members': pending_members,
            'expired_members': expired_members,
            'active_rate': active_rate,
            'expiring_soon': expiring_soon,
            'rookie_count': GymMembership.objects.filter(membership_plan='rookie').count(),
            'warrior_count': GymMembership.objects.filter(membership_plan='warrior').count(),
            'elite_count': GymMembership.objects.filter(membership_plan='elite').count(),
        }

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_year = timezone.now().year

        # Monthly expense data
        expense_labels = []
        expense_data = []

        for month in range(1, 13):
            total = Expense.objects.filter(
                date__month=month,
                date__year=current_year
            ).aggregate(
                total=Sum('price')
            )['total'] or 0

            expense_labels.append(calendar.month_abbr[month])
            expense_data.append(float(total))

        context['expense_labels'] = json.dumps(expense_labels)
        context['expense_data'] = json.dumps(expense_data)

        # Cash data (you can adjust this based on your logic)
        # This could be income data for comparison
        cash_data = []
        for month in range(1, 13):
            # Example: using income as cash data
            total = Income.objects.filter(
                date_received__month=month,
                date_received__year=current_year
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0
            cash_data.append(float(total))

        context['cash_data'] = json.dumps(cash_data)

        # Dashboard summary data
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0

        context['dashboard'] = {
            'cash_at_hand': total_expenses,  # Adjust based on your logic
            'cash_at_bank': total_income,    # Adjust based on your logic
            'expenses': total_expenses,
            'total_sales': total_income,
        }

        return context

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'GodMode/expense_form.html'
    success_url = reverse_lazy('godmode:expenses')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get expense category distribution for donut chart
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta

        # Group expenses by name (as categories)
        expense_categories = Expense.objects.values('name').annotate(
            total=Sum('price')
        ).order_by('-total')[:6]

        category_labels = [item['name'] for item in expense_categories]
        category_data = [float(item['total']) for item in expense_categories]

        # If no categories, provide placeholder
        if not category_labels:
            category_labels = ['No Data']
            category_data = [0]

        context['expense_category_labels'] = json.dumps(category_labels)
        context['expense_category_data'] = json.dumps(category_data)

        # Dashboard stats
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0
        expense_count = Expense.objects.count()

        # Monthly expenses
        now = timezone.now()
        month_start = timezone.datetime(now.year, now.month, 1)
        monthly_expenses = Expense.objects.filter(
            date__gte=month_start
        ).aggregate(total=Sum('price'))['total'] or 0

        # Weekly expenses
        week_start = now - timedelta(days=now.weekday())
        weekly_expenses = Expense.objects.filter(
            date__gte=week_start
        ).aggregate(total=Sum('price'))['total'] or 0

        # Average expense
        if expense_count > 0:
            avg_expense = round(total_expenses / expense_count, 2)
        else:
            avg_expense = 0

        # Highest expense
        highest_expense = Expense.objects.aggregate(max_price=Sum('price'))['max_price'] or 0

        # Monthly change (compare with last month)
        last_month = now - timedelta(days=30)
        last_month_start = timezone.datetime(last_month.year, last_month.month, 1)
        last_month_expenses = Expense.objects.filter(
            date__gte=last_month_start,
            date__lt=month_start
        ).aggregate(total=Sum('price'))['total'] or 0

        if last_month_expenses > 0:
            monthly_change = round(((monthly_expenses - last_month_expenses) / last_month_expenses) * 100, 1)
        else:
            monthly_change = 0

        # Top categories for sidebar
        top_categories = Expense.objects.values('name').annotate(
            total=Sum('price')
        ).order_by('-total')[:5]

        context['dashboard'] = {
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'weekly_expenses': weekly_expenses,
            'avg_expense': avg_expense,
            'expense_count': expense_count,
            'highest_expense': highest_expense,
            'monthly_change': monthly_change,
            'top_categories': top_categories,
        }

        return context


class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'GodMode/expense_form.html'
    success_url = reverse_lazy('godmode:expenses')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get expense category distribution for donut chart
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta

        # Group expenses by name (as categories)
        expense_categories = Expense.objects.values('name').annotate(
            total=Sum('price')
        ).order_by('-total')[:6]

        category_labels = [item['name'] for item in expense_categories]
        category_data = [float(item['total']) for item in expense_categories]

        # If no categories, provide placeholder
        if not category_labels:
            category_labels = ['No Data']
            category_data = [0]

        context['expense_category_labels'] = json.dumps(category_labels)
        context['expense_category_data'] = json.dumps(category_data)

        # Dashboard stats
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0
        expense_count = Expense.objects.count()

        # Monthly expenses
        now = timezone.now()
        month_start = timezone.datetime(now.year, now.month, 1)
        monthly_expenses = Expense.objects.filter(
            date__gte=month_start
        ).aggregate(total=Sum('price'))['total'] or 0

        # Weekly expenses
        week_start = now - timedelta(days=now.weekday())
        weekly_expenses = Expense.objects.filter(
            date__gte=week_start
        ).aggregate(total=Sum('price'))['total'] or 0

        # Average expense
        if expense_count > 0:
            avg_expense = round(total_expenses / expense_count, 2)
        else:
            avg_expense = 0

        # Highest expense
        highest_expense = Expense.objects.aggregate(max_price=Sum('price'))['max_price'] or 0

        # Monthly change (compare with last month)
        last_month = now - timedelta(days=30)
        last_month_start = timezone.datetime(last_month.year, last_month.month, 1)
        last_month_expenses = Expense.objects.filter(
            date__gte=last_month_start,
            date__lt=month_start
        ).aggregate(total=Sum('price'))['total'] or 0

        if last_month_expenses > 0:
            monthly_change = round(((monthly_expenses - last_month_expenses) / last_month_expenses) * 100, 1)
        else:
            monthly_change = 0

        # Top categories for sidebar
        top_categories = Expense.objects.values('name').annotate(
            total=Sum('price')
        ).order_by('-total')[:5]

        context['dashboard'] = {
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'weekly_expenses': weekly_expenses,
            'avg_expense': avg_expense,
            'expense_count': expense_count,
            'highest_expense': highest_expense,
            'monthly_change': monthly_change,
            'top_categories': top_categories,
        }

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_year = timezone.now().year

        # Monthly income data
        income_labels = []
        income_data = []

        for month in range(1, 13):
            total = Income.objects.filter(
                date_received__month=month,
                date_received__year=current_year
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            income_labels.append(calendar.month_abbr[month])
            income_data.append(float(total))

        context['income_labels'] = json.dumps(income_labels)
        context['income_data'] = json.dumps(income_data)

        # Monthly expense data for comparison
        expense_data = []
        for month in range(1, 13):
            total = Expense.objects.filter(
                date__month=month,
                date__year=current_year
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            expense_data.append(float(total))

        context['expense_data'] = json.dumps(expense_data)

        # Dashboard summary data
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0

        context['dashboard'] = {
            'cash_at_hand': total_income,  # Assuming cash at hand is total income
            'cash_at_bank': total_income,  # Adjust based on your logic
            'total_income': total_income,
            'net_profit': total_income - total_expenses,
        }

        return context


class IncomeCreateView(CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'GodMode/income_form.html'
    success_url = reverse_lazy('godmode:incomes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get income source distribution for donut chart
        from django.db.models import Sum

        income_sources = Income.objects.values('source').annotate(
            total=Sum('amount')
        ).exclude(source__isnull=True).exclude(source='').order_by('-total')[:6]

        source_labels = [item['source'] for item in income_sources]
        source_data = [float(item['total']) for item in income_sources]

        # If no sources, provide placeholder
        if not source_labels:
            source_labels = ['No Data']
            source_data = [0]

        context['income_source_labels'] = json.dumps(source_labels)
        context['income_source_data'] = json.dumps(source_data)

        # Dashboard stats
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0
        income_count = Income.objects.count()
        unique_sources = Income.objects.values('source').distinct().exclude(source__isnull=True).exclude(source='').count()

        # Monthly average (last 12 months)
        from django.utils import timezone
        from datetime import timedelta

        twelve_months_ago = timezone.now().date() - timedelta(days=365)
        monthly_total = Income.objects.filter(
            date_received__gte=twelve_months_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_average = round(monthly_total / 12, 2)

        # Highest income
        highest_income = Income.objects.aggregate(max_amount=Sum('amount'))['max_amount'] or 0

        context['dashboard'] = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': total_income - total_expenses,
            'income_count': income_count,
            'monthly_average': monthly_average,
            'highest_income': highest_income,
            'unique_sources': unique_sources,
        }

        return context


class IncomeUpdateView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'GodMode/income_form.html'
    success_url = reverse_lazy('godmode:incomes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get income source distribution for donut chart
        from django.db.models import Sum

        income_sources = Income.objects.values('source').annotate(
            total=Sum('amount')
        ).exclude(source__isnull=True).exclude(source='').order_by('-total')[:6]

        source_labels = [item['source'] for item in income_sources]
        source_data = [float(item['total']) for item in income_sources]

        # If no sources, provide placeholder
        if not source_labels:
            source_labels = ['No Data']
            source_data = [0]

        context['income_source_labels'] = json.dumps(source_labels)
        context['income_source_data'] = json.dumps(source_data)

        # Dashboard stats
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = Expense.objects.aggregate(total=Sum('price'))['total'] or 0
        income_count = Income.objects.count()
        unique_sources = Income.objects.values('source').distinct().exclude(source__isnull=True).exclude(source='').count()

        # Monthly average (last 12 months)
        from django.utils import timezone
        from datetime import timedelta

        twelve_months_ago = timezone.now().date() - timedelta(days=365)
        monthly_total = Income.objects.filter(
            date_received__gte=twelve_months_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_average = round(monthly_total / 12, 2)

        # Highest income
        highest_income = Income.objects.aggregate(max_amount=Sum('amount'))['max_amount'] or 0

        context['dashboard'] = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': total_income - total_expenses,
            'income_count': income_count,
            'monthly_average': monthly_average,
            'highest_income': highest_income,
            'unique_sources': unique_sources,
        }

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get daily check-in data for the last 30 days
        checkin_labels = []
        checkin_data = []

        for i in range(6, -1, -1):
            day = timezone.now().date() - timedelta(days=i)
            total = DailyCheckIn.objects.filter(checkin_date=day).count()
            checkin_labels.append(day.strftime('%d %b'))
            checkin_data.append(total)

        context['checkin_labels'] = json.dumps(checkin_labels)
        context['checkin_data'] = json.dumps(checkin_data)

        # Get status distribution
        status_labels = ['Present', 'Late', 'Absent', 'Missed']
        status_data = [
            DailyCheckIn.objects.filter(status='present').count(),
            DailyCheckIn.objects.filter(status='late').count(),
            DailyCheckIn.objects.filter(status='absent').count(),
            DailyCheckIn.objects.filter(status='missed').count()
        ]

        context['status_labels'] = json.dumps(status_labels)
        context['status_data'] = json.dumps(status_data)

        # Dashboard stats
        total_checkins = DailyCheckIn.objects.count()
        today_checkins = DailyCheckIn.objects.filter(checkin_date=timezone.now().date()).count()
        active_members = GymMembership.objects.filter(status='active').count()

        # Calculate check-in rate (today's check-ins / active members * 100)
        if active_members > 0:
            checkin_rate = round((today_checkins / active_members) * 100, 1)
        else:
            checkin_rate = 0

        context['dashboard'] = {
            'total_checkins': total_checkins,
            'today_checkins': today_checkins,
            'active_members': active_members,
            'checkin_rate': checkin_rate,
        }

        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get inventory by condition
        condition_labels = ['Good', 'Maintenance', 'Faulty']
        condition_data = [
            Inventory.objects.filter(condition='good').count(),
            Inventory.objects.filter(condition='maintenance').count(),
            Inventory.objects.filter(condition='faulty').count()
        ]

        context['condition_labels'] = json.dumps(condition_labels)
        context['condition_data'] = json.dumps(condition_data)

        # Get inventory by brand (top 10 brands)
        from django.db.models import Count

        brand_counts = Inventory.objects.values('brand').annotate(
            count=Count('id')
        ).exclude(brand__isnull=True).exclude(brand='').order_by('-count')[:10]

        brand_labels = [item['brand'] for item in brand_counts]
        brand_data = [item['count'] for item in brand_counts]

        # If no brands, provide placeholder data
        if not brand_labels:
            brand_labels = ['No Brands']
            brand_data = [0]

        context['brand_labels'] = json.dumps(brand_labels)
        context['brand_data'] = json.dumps(brand_data)

        # Dashboard stats
        total_items = Inventory.objects.count()
        good_items = Inventory.objects.filter(condition='good').count()
        maintenance_items = Inventory.objects.filter(condition='maintenance').count()
        faulty_items = Inventory.objects.filter(condition='faulty').count()

        context['dashboard'] = {
            'total_items': total_items,
            'good_items': good_items,
            'maintenance_items': maintenance_items,
            'faulty_items': faulty_items,
        }

        return context



class InventoryCreateView(CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "GodMode/inventory_form.html"
    success_url = reverse_lazy('godmode:inventory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard stats for the form page
        context['dashboard'] = {
            'total_items': Inventory.objects.count(),
            'good_items': Inventory.objects.filter(condition='good').count(),
            'maintenance_items': Inventory.objects.filter(condition='maintenance').count(),
            'faulty_items': Inventory.objects.filter(condition='faulty').count(),
        }

        return context


class InventoryUpdateView(UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "GodMode/inventory_form.html"
    success_url = reverse_lazy('godmode:inventory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard stats for the form page
        context['dashboard'] = {
            'total_items': Inventory.objects.count(),
            'good_items': Inventory.objects.filter(condition='good').count(),
            'maintenance_items': Inventory.objects.filter(condition='maintenance').count(),
            'faulty_items': Inventory.objects.filter(condition='faulty').count(),
        }

        return context


class InventoryDeleteView(DeleteView):
    model = Inventory
    success_url = reverse_lazy('godmode:inventory')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)