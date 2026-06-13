from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Sum, Count
import json
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm
from home.models import (
    User, GymMembership, WorkoutLog, WeightLog,
    BodyMetrics, PersonalBest, PointsTransaction, UserStreak,
    UserSettings, Testimonial
)
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Save the user (profile will be created automatically via signal)
        user = form.save()

        # Add success message with account type
        account_type = form.cleaned_data.get('account_type')
        messages.success(
            self.request,
            f'Registration successful! You registered as a {account_type}. Please log in.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        # Get the username and password from the form
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        # Authenticate the user
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.username}!')

            # Redirect to next parameter if exists
            next_url = self.request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid username or password.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')

class ProfileView(LoginRequiredMixin, TemplateView):
    """User Profile Dashboard - Reads from Database"""
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get or create related objects
        profile = user.profile if hasattr(user, 'profile') else None
        membership = GymMembership.objects.filter(user=user).first()
        streak = user.streak if hasattr(user, 'streak') else None
        settings = user.settings if hasattr(user, 'settings') else None

        # Create default membership if none exists
        if not membership:
            membership = GymMembership.objects.create(
                user=user,
                membership_plan='rookie',
                status='active'
            )

        # ===== WORKOUT STATISTICS (From Database) =====
        workout_count = WorkoutLog.objects.filter(user=user).count()
        total_calories = WorkoutLog.objects.filter(user=user).aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0

        # Current streak from UserStreak model
        current_streak = streak.current_streak if streak else 0

        # Points from database
        total_points = PointsTransaction.objects.filter(user=user).aggregate(Sum('points'))['points__sum'] or 0

        # ===== WEIGHT DATA (From Database) =====
        latest_weight = WeightLog.objects.filter(user=user).order_by('-date').first()
        first_weight = WeightLog.objects.filter(user=user).order_by('date').first()
        current_weight = float(latest_weight.weight) if latest_weight else 188
        start_weight = float(first_weight.weight) if first_weight else 215

        # Goal weight from profile
        goal_weight = profile.goal_weight if profile and profile.goal_weight else 175
        weight_lost = start_weight - current_weight

        # ===== BODY METRICS (From Database) =====
        latest_metrics = BodyMetrics.objects.filter(user=user).order_by('-date').first()
        body_fat = float(latest_metrics.body_fat) if latest_metrics and latest_metrics.body_fat else 18.4
        muscle_mass = float(latest_metrics.muscle_mass) if latest_metrics and latest_metrics.muscle_mass else 153
        bmi = float(latest_metrics.bmi) if latest_metrics and latest_metrics.bmi else self.calculate_bmi(current_weight)

        # Last measured date
        last_measured = latest_metrics.date if latest_metrics else timezone.now().date()

        # ===== MEMBERSHIP INFO =====
        plan_display = {
            'rookie': {'name': 'ROOKIE', 'icon': '💪', 'price': 39},
            'warrior': {'name': 'WARRIOR', 'icon': '⚡', 'price': 79},
            'elite': {'name': 'ELITE', 'icon': '🏆', 'price': 129},
        }
        current_plan = membership.membership_plan
        plan_info = plan_display.get(current_plan, plan_display['warrior'])

        # Next billing date (30 days from membership start or last payment)
        next_billing = membership.last_payment_date + timedelta(days=30) if membership.last_payment_date else timezone.now() + timedelta(days=30)

        # ===== PT SESSIONS =====
        pt_used = 1
        pt_total = 2 if current_plan == 'warrior' else (0 if current_plan == 'rookie' else 100)
        pt_remaining = pt_total - pt_used

        # ===== WEIGHT HISTORY (From Database) =====
        weight_history = self.get_weight_history_from_db(user)

        # ===== RECENT WORKOUTS (From Database) =====
        recent_workouts = self.get_recent_workouts_from_db(user)

        # ===== PERSONAL BESTS (From Database) =====
        personal_bests = self.get_personal_bests_from_db(user)

        # ===== STRENGTH PROGRESS (From Database) =====
        strength_progress = self.get_strength_progress_from_db(user)

        # ===== CARDIO PROGRESS (From Database) =====
        cardio_progress = self.get_cardio_progress_from_db(user)

        # ===== WORKOUT SPLIT (From Database) =====
        workout_split = self.get_workout_split_from_db(user)

        # ===== MONTHLY GOAL PROGRESS (From Database) =====
        monthly_goal_progress = self.get_monthly_goal_progress_from_db(user)

        # ===== WEEKLY GOALS (From Database) =====
        weekly_goals = self.get_weekly_goals_from_db(user)

        # ===== ACTIVITY HEATMAP (From Database) =====
        heatmap_data = self.get_heatmap_data_from_db(user)

        # ===== BENEFITS BASED ON PLAN =====
        benefits = self.get_plan_benefits(current_plan)

        # Get initials for avatar
        initials = self.get_initials(user)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        # Notification settings
        notification_settings = {
            'workout_reminders': settings.workout_reminders if settings else True,
            'pt_alerts': settings.pt_alerts if settings else True,
            'weight_reminder': settings.weight_reminder if settings else True,
            'promo_emails': settings.promo_emails if settings else False,
            'class_confirmations': settings.class_confirmations if settings else True,
        }

        # Membership status
        membership_status = 'Active' if membership.status == 'active' else 'Inactive'

        # Context data for template
        context.update({
            # User info
            'user': user,
            'profile': profile,
            'membership': membership,
            'member_since': user.date_joined,
            'member_id': f"ATM-{user.id:04d}",
            'full_name': full_name,
            'initials': initials,
            'plan_icon': plan_info['icon'],
            'plan_name': plan_info['name'],
            'membership_status': membership_status,

            # Stats (from DB)
            'workout_count': workout_count,
            'current_streak': current_streak,
            'weight_lost': round(weight_lost, 1),
            'points_earned': total_points,
            'total_calories': total_calories,

            # Weight data (from DB)
            'current_weight': current_weight,
            'start_weight': start_weight,
            'goal_weight': goal_weight,
            'bmi': bmi,
            'body_fat': body_fat,
            'muscle_mass': muscle_mass,
            'last_measured': last_measured.strftime('%b %d, %Y'),

            # Plan info
            'plan_price': plan_info['price'],
            'next_billing': next_billing,
            'payment_method': membership.payment_method or "Visa ···· 4892",
            'auto_renew': membership.status == 'active',

            # Plan features
            'benefits': benefits,
            'pt_used': pt_used,
            'pt_total': pt_total,
            'pt_remaining': pt_remaining,

            # Goals progress
            'monthly_goal_progress': monthly_goal_progress,
            'weekly_goals': weekly_goals,

            # Chart data (as JSON strings)
            'weight_history': json.dumps(weight_history),
            'strength_progress': json.dumps(strength_progress),
            'cardio_progress': json.dumps(cardio_progress),
            'workout_split': json.dumps(workout_split),

            # Recent data
            'recent_workouts': recent_workouts,
            'personal_bests': personal_bests,
            'heatmap_data': heatmap_data,

            # Notification settings
            'notifications': notification_settings,

            # Form data for settings tab
            'user_form_data': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': profile.phone if profile else user.phone,
                'birth_date': profile.birth_date.isoformat() if profile and profile.birth_date else None,
                'goal_weight': goal_weight,
            }
        })

        return context

    def get_initials(self, user):
        """Get user initials for avatar"""
        if user.first_name and user.last_name:
            return f"{user.first_name[0]}{user.last_name[0]}".upper()
        elif user.first_name:
            return user.first_name[:2].upper()
        else:
            return user.username[:2].upper()

    def calculate_bmi(self, weight_lbs, height_inches=70):
        """Calculate BMI from weight in lbs and height in inches"""
        bmi = (weight_lbs / (height_inches ** 2)) * 703
        return round(bmi, 1)

    def get_weight_history_from_db(self, user):
        """Get weight history from database for charts"""
        weight_logs = WeightLog.objects.filter(user=user).order_by('date')[:30]

        if weight_logs.exists():
            labels = [log.date.strftime('%b %d') for log in weight_logs]
            data = [float(log.weight) for log in weight_logs]

            return {
                '1m': {'labels': labels[-9:], 'data': data[-9:]},
                '3m': {'labels': labels[::3][-7:], 'data': data[::3][-7:]},
                '6m': {'labels': [log.strftime('%b') for log in labels if log][-6:], 'data': data[-6:]},
                '1y': {'labels': [log.strftime('%b') for log in labels][-12:], 'data': data[-12:]},
            }

        # Return default data if no logs exist
        return {
            '1m': {'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'], 'data': [195, 192, 190, 188]},
            '3m': {'labels': ['Jan', 'Feb', 'Mar'], 'data': [200, 195, 188]},
            '6m': {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'data': [212, 208, 205, 200, 194, 188]},
            '1y': {'labels': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'data': [215, 213, 211, 210, 209, 207, 212, 208, 205, 200, 194, 188]}
        }

    def get_recent_workouts_from_db(self, user):
        """Get recent workouts from database"""
        workouts = WorkoutLog.objects.filter(user=user).order_by('-date')[:10]

        result = []
        for w in workouts:
            result.append({
                'day': w.date.strftime('%d'),
                'month': w.date.strftime('%b').upper(),
                'title': w.title,
                'subtitle': w.notes[:50] if w.notes else w.get_workout_type_display(),
                'type': w.get_workout_type_display(),
                'duration': w.duration_minutes,
                'calories': w.calories_burned,
            })
        return result

    def get_personal_bests_from_db(self, user):
        """Get personal bests from database"""
        pbs = PersonalBest.objects.filter(user=user, is_current=True)

        result = []
        for pb in pbs:
            is_new = pb.date >= (timezone.now().date() - timedelta(days=7))
            result.append({
                'exercise': pb.get_exercise_display(),
                'value': pb.value,
                'unit': pb.unit,
                'date': pb.date.strftime('%b %d'),
                'is_new': is_new,
            })
        return result

    def get_strength_progress_from_db(self, user):
        """Get strength progress from workout logs"""
        strength_workouts = WorkoutLog.objects.filter(
            user=user,
            workout_type='strength',
            date__gte=timezone.now().date() - timedelta(days=180)
        )

        if strength_workouts.exists():
            monthly_data = {}
            for w in strength_workouts:
                month_key = w.date.strftime('%b')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + 1

            months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            labels = [m for m in months_order if m in monthly_data]
            data = [monthly_data[m] for m in labels]

            return {'labels': labels, 'data': data}

        return {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'data': [88, 95, 102, 110, 118, 126]}

    def get_cardio_progress_from_db(self, user):
        """Get cardio progress from workout logs"""
        cardio_workouts = WorkoutLog.objects.filter(
            user=user,
            workout_type='cardio',
            date__gte=timezone.now().date() - timedelta(days=180)
        )

        if cardio_workouts.exists():
            monthly_data = {}
            for w in cardio_workouts:
                month_key = w.date.strftime('%b')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + w.duration_minutes

            months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            labels = [m for m in months_order if m in monthly_data]
            data = [monthly_data[m] for m in labels]

            return {'labels': labels, 'data': data}

        return {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'data': [180, 210, 240, 270, 300, 310]}

    def get_workout_split_from_db(self, user):
        """Get workout type distribution from database"""
        workout_counts = WorkoutLog.objects.filter(user=user).values('workout_type').annotate(count=Count('id'))

        if workout_counts.exists():
            type_map = {
                'strength': 'Strength',
                'hiit': 'HIIT',
                'cardio': 'Cardio',
                'combat': 'Combat',
                'yoga': 'Yoga',
            }
            total = sum(item['count'] for item in workout_counts)
            labels = []
            data = []
            for item in workout_counts:
                if total > 0:
                    labels.append(type_map.get(item['workout_type'], item['workout_type']))
                    data.append(round((item['count'] / total) * 100))

            return {'labels': labels, 'data': data}

        return {'labels': ['Strength', 'HIIT', 'Cardio', 'Combat', 'Yoga'], 'data': [42, 20, 18, 12, 8]}

    def get_monthly_goal_progress_from_db(self, user):
        """Calculate monthly goal progress from database"""
        current_month = timezone.now().month
        current_year = timezone.now().year

        month_workouts = WorkoutLog.objects.filter(
            user=user,
            date__year=current_year,
            date__month=current_month
        )

        sessions_completed = month_workouts.count()
        sessions_goal = 24

        total_calories = month_workouts.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        calories_goal = 15000

        active_days = month_workouts.values('date').distinct().count()
        active_days_goal = 26

        return {
            'sessions_completed': sessions_completed,
            'sessions_goal': sessions_goal,
            'percentage': round((sessions_completed / sessions_goal) * 100) if sessions_goal > 0 else 0,
            'calories_burned': total_calories,
            'calories_goal': calories_goal,
            'calories_percentage': round((total_calories / calories_goal) * 100) if calories_goal > 0 else 0,
            'active_days': active_days,
            'active_days_goal': active_days_goal,
            'active_days_percentage': round((active_days / active_days_goal) * 100) if active_days_goal > 0 else 0,
        }

    def get_weekly_goals_from_db(self, user):
        """Calculate weekly goals from database"""
        current_week = timezone.now().isocalendar()[1]
        current_year = timezone.now().year

        week_workouts = WorkoutLog.objects.filter(
            user=user,
            date__year=current_year,
            date__week=current_week
        )

        workouts_completed = week_workouts.count()
        workouts_goal = 5

        cardio_minutes = week_workouts.filter(workout_type='cardio').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        cardio_goal = 120

        strength_sets = week_workouts.filter(workout_type='strength').count()
        strength_goal = 30

        calories_burned = week_workouts.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        calories_goal = 3000

        water_intake = 2.4
        water_goal = 3.0

        return [
            {'label': 'Workouts', 'current': workouts_completed, 'goal': workouts_goal, 'percentage': round((workouts_completed / workouts_goal) * 100) if workouts_goal > 0 else 0},
            {'label': 'Cardio (mins)', 'current': cardio_minutes, 'goal': cardio_goal, 'percentage': round((cardio_minutes / cardio_goal) * 100) if cardio_goal > 0 else 0},
            {'label': 'Strength Sets', 'current': strength_sets, 'goal': strength_goal, 'percentage': round((strength_sets / strength_goal) * 100) if strength_goal > 0 else 0},
            {'label': 'Calories Out', 'current': calories_burned, 'goal': calories_goal, 'percentage': round((calories_burned / calories_goal) * 100) if calories_goal > 0 else 0},
            {'label': 'Water (L)', 'current': water_intake, 'goal': water_goal, 'percentage': round((water_intake / water_goal) * 100) if water_goal > 0 else 0},
        ]

    def get_heatmap_data_from_db(self, user):
        """Generate activity heatmap from database"""
        twelve_weeks_ago = timezone.now().date() - timedelta(days=84)
        workouts = WorkoutLog.objects.filter(
            user=user,
            date__gte=twelve_weeks_ago
        ).values('date')

        workout_dates = {}
        for w in workouts:
            workout_dates[w['date']] = workout_dates.get(w['date'], 0) + 1

        heatmap = []
        current_date = twelve_weeks_ago

        while current_date <= timezone.now().date():
            day_workouts = workout_dates.get(current_date, 0)
            if day_workouts == 0:
                intensity = 0
            elif day_workouts <= 1:
                intensity = 1
            elif day_workouts == 2:
                intensity = 2
            elif day_workouts == 3:
                intensity = 3
            else:
                intensity = 4

            heatmap.append(intensity)
            current_date += timedelta(days=1)

        return heatmap

    def get_plan_benefits(self, plan):
        """Get benefits for a membership plan"""
        benefits_map = {
            'rookie': [
                {'name': 'Full Gym Access', 'included': True},
                {'name': 'Cardio Equipment', 'included': True},
                {'name': 'Locker Room Access', 'included': True},
                {'name': 'Group Classes', 'included': False, 'value': '0'},
                {'name': 'PT Sessions', 'included': False, 'value': '0'},
                {'name': 'Guest Passes', 'included': True, 'value': '1 / month'},
                {'name': 'Sauna Access', 'included': False},
                {'name': 'Nutrition Bar', 'included': False},
            ],
            'warrior': [
                {'name': 'Full Gym Access', 'included': True},
                {'name': 'Cardio Equipment', 'included': True},
                {'name': 'Locker Room & Sauna', 'included': True},
                {'name': 'Group Classes', 'included': True, 'value': 'Unlimited'},
                {'name': 'PT Sessions', 'included': True, 'value': '2 / month'},
                {'name': 'Guest Passes', 'included': True, 'value': '3 / month'},
                {'name': 'Sauna Access', 'included': True},
                {'name': 'Nutrition Bar', 'included': True},
            ],
            'elite': [
                {'name': 'Full Gym Access', 'included': True},
                {'name': 'All Equipment & Classes', 'included': True},
                {'name': 'Sauna, Ice Bath & Recovery', 'included': True},
                {'name': 'Group Classes', 'included': True, 'value': 'Unlimited'},
                {'name': 'PT Sessions', 'included': True, 'value': 'Unlimited'},
                {'name': 'Guest Passes', 'included': True, 'value': 'Unlimited'},
                {'name': 'Full Nutrition Program', 'included': True},
                {'name': 'Priority Booking', 'included': True},
            ],
        }
        return benefits_map.get(plan, benefits_map['warrior'])


class UpdateProfileView(LoginRequiredMixin, View):
    """Handle profile updates via AJAX"""

    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        try:
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            user.save()

            profile = user.profile if hasattr(user, 'profile') else None
            if profile:
                if 'birth_date' in data and data['birth_date']:
                    profile.birth_date = data['birth_date']
                if 'goal_weight' in data:
                    profile.goal_weight = data['goal_weight']
                if 'phone' in data:
                    profile.phone = data['phone']
                profile.save()

            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class UpdateNotificationSettingsView(LoginRequiredMixin, View):
    """Handle notification settings updates"""

    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        try:
            settings = user.settings if hasattr(user, 'settings') else None
            if settings:
                if 'workout_reminders' in data:
                    settings.workout_reminders = data['workout_reminders']
                if 'pt_alerts' in data:
                    settings.pt_alerts = data['pt_alerts']
                if 'weight_reminder' in data:
                    settings.weight_reminder = data['weight_reminder']
                if 'promo_emails' in data:
                    settings.promo_emails = data['promo_emails']
                if 'class_confirmations' in data:
                    settings.class_confirmations = data['class_confirmations']
                settings.save()

            return JsonResponse({'success': True, 'message': 'Settings updated successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class LogWorkoutView(LoginRequiredMixin, View):
    """Handle workout logging via AJAX"""

    def post(self, request):
        data = json.loads(request.body)

        try:
            workout = WorkoutLog.objects.create(
                user=request.user,
                workout_type=data.get('workout_type', 'strength'),
                title=data.get('title', 'Workout Session'),
                notes=data.get('notes', ''),
                duration_minutes=data.get('duration', 60),
                calories_burned=data.get('calories', 400),
                date=data.get('date', timezone.now().date())
            )

            PointsTransaction.objects.create(
                user=request.user,
                points=50,
                transaction_type='workout',
                description=f"Completed {workout.get_workout_type_display()} workout"
            )

            streak = request.user.streak if hasattr(request.user, 'streak') else None
            if streak:
                today = timezone.now().date()
                if streak.last_workout_date == today - timedelta(days=1):
                    streak.current_streak += 1
                    if streak.current_streak > streak.longest_streak:
                        streak.longest_streak = streak.current_streak
                elif streak.last_workout_date != today:
                    streak.current_streak = 1
                streak.last_workout_date = today
                streak.save()

            return JsonResponse({'success': True, 'message': 'Workout logged successfully! +50 points'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)



class UpdateProfileView(LoginRequiredMixin, View):
    """Handle profile updates via AJAX - Saves to Database"""

    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        try:
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            user.save()

            # Update profile
            profile = user.profile if hasattr(user, 'profile') else None
            if profile:
                if 'birth_date' in data and data['birth_date']:
                    profile.birth_date = data['birth_date']
                if 'goal_weight' in data:
                    profile.goal_weight = data['goal_weight']
                if 'phone' in data:
                    profile.phone = data['phone']
                profile.save()

            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class UpdateNotificationSettingsView(LoginRequiredMixin, View):
    """Handle notification settings updates - Saves to Database"""

    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        try:
            settings = user.settings if hasattr(user, 'settings') else None
            if settings:
                if 'workout_reminders' in data:
                    settings.workout_reminders = data['workout_reminders']
                if 'pt_alerts' in data:
                    settings.pt_alerts = data['pt_alerts']
                if 'weight_reminder' in data:
                    settings.weight_reminder = data['weight_reminder']
                if 'promo_emails' in data:
                    settings.promo_emails = data['promo_emails']
                if 'class_confirmations' in data:
                    settings.class_confirmations = data['class_confirmations']
                settings.save()

            return JsonResponse({'success': True, 'message': 'Settings updated successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class LogWorkoutView(LoginRequiredMixin, View):
    """Handle workout logging via AJAX - Saves to Database"""

    def post(self, request):
        data = json.loads(request.body)

        try:
            workout = WorkoutLog.objects.create(
                user=request.user,
                workout_type=data.get('workout_type', 'strength'),
                title=data.get('title', 'Workout Session'),
                notes=data.get('notes', ''),
                duration_minutes=data.get('duration', 60),
                calories_burned=data.get('calories', 400),
                date=data.get('date', timezone.now().date())
            )

            # Add points for workout
            PointsTransaction.objects.create(
                user=request.user,
                points=50,
                transaction_type='workout',
                description=f"Completed {workout.get_workout_type_display()} workout"
            )

            # Update streak
            streak = request.user.streak if hasattr(request.user, 'streak') else None
            if streak:
                today = timezone.now().date()
                if streak.last_workout_date == today - timedelta(days=1):
                    streak.current_streak += 1
                    if streak.current_streak > streak.longest_streak:
                        streak.longest_streak = streak.current_streak
                elif streak.last_workout_date != today:
                    streak.current_streak = 1
                streak.last_workout_date = today
                streak.save()

            return JsonResponse({'success': True, 'message': 'Workout logged successfully! +50 points'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class AddWeightView(LoginRequiredMixin, View):
    """Handle weight logging via AJAX"""

    def post(self, request):
        data = json.loads(request.body)

        try:
            weight_log, created = WeightLog.objects.get_or_create(
                user=request.user,
                date=data.get('date', timezone.now().date()),
                defaults={'weight': data.get('weight', 0)}
            )

            if not created:
                weight_log.weight = data.get('weight', weight_log.weight)
                weight_log.save()

            return JsonResponse({'success': True, 'message': 'Weight logged successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)