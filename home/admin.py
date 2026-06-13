from django.contrib import admin
from .models import (
    ContactMessage, GymMembership, WorkoutLog, WeightLog,
    BodyMetrics, PersonalBest, PointsTransaction, UserStreak,
    UserSettings, Testimonial
)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Contact message admin"""

    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Sender Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'is_read')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = "Mark selected messages as unread"


@admin.register(GymMembership)
class GymMembershipAdmin(admin.ModelAdmin):
    """Gym Membership admin"""

    list_display = ('user_display', 'membership_plan', 'status', 'start_date', 'end_date', 'payment_method')
    list_filter = ('membership_plan', 'status', 'start_date')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'start_date')

    fieldsets = (
        ('Member Information', {
            'fields': ('user',)
        }),
        ('Membership Details', {
            'fields': ('membership_plan', 'status', 'start_date', 'end_date')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'last_payment_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_display(self, obj):
        return f"{obj.user.get_full_name() or obj.user.username} ({obj.user.email})"
    user_display.short_description = 'Member'
    user_display.admin_order_field = 'user__username'

    actions = ['activate_membership', 'cancel_membership']

    def activate_membership(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} memberships activated.')
    activate_membership.short_description = "Activate selected memberships"

    def cancel_membership(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} memberships cancelled.')
    cancel_membership.short_description = "Cancel selected memberships"


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    """Workout Log admin"""

    list_display = ('user', 'workout_type', 'title', 'duration_minutes', 'calories_burned', 'date')
    list_filter = ('workout_type', 'date', 'user')
    search_fields = ('user__username', 'user__email', 'title', 'notes')
    list_select_related = ('user',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Workout Information', {
            'fields': ('user', 'workout_type', 'title', 'date')
        }),
        ('Workout Details', {
            'fields': ('duration_minutes', 'calories_burned', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)


@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    """Weight Log admin"""

    list_display = ('user', 'weight', 'date', 'notes')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email', 'notes')
    list_select_related = ('user',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Weight Information', {
            'fields': ('user', 'weight', 'date', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)


@admin.register(BodyMetrics)
class BodyMetricsAdmin(admin.ModelAdmin):
    """Body Metrics admin"""

    list_display = ('user', 'body_fat', 'muscle_mass', 'bmi', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Metrics Information', {
            'fields': ('user', 'body_fat', 'muscle_mass', 'bmi', 'date')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)


@admin.register(PersonalBest)
class PersonalBestAdmin(admin.ModelAdmin):
    """Personal Best admin"""

    list_display = ('user', 'exercise_display', 'value', 'unit', 'date', 'is_current')
    list_filter = ('exercise', 'is_current', 'date')
    search_fields = ('user__username', 'user__email', 'value')
    list_select_related = ('user',)
    list_editable = ('is_current',)

    def exercise_display(self, obj):
        return obj.get_exercise_display()
    exercise_display.short_description = 'Exercise'
    exercise_display.admin_order_field = 'exercise'

    fieldsets = (
        ('Personal Best Information', {
            'fields': ('user', 'exercise', 'value', 'unit', 'date', 'is_current')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    actions = ['mark_as_current', 'mark_as_not_current']

    def mark_as_current(self, request, queryset):
        updated = queryset.update(is_current=True)
        self.message_user(request, f'{updated} records marked as current.')
    mark_as_current.short_description = "Mark as current"

    def mark_as_not_current(self, request, queryset):
        updated = queryset.update(is_current=False)
        self.message_user(request, f'{updated} records marked as not current.')
    mark_as_not_current.short_description = "Mark as not current"


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    """Points Transaction admin"""

    list_display = ('user', 'points', 'transaction_type', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    list_select_related = ('user',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Transaction Information', {
            'fields': ('user', 'points', 'transaction_type', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    """User Streak admin"""

    list_display = ('user', 'current_streak', 'longest_streak', 'last_workout_date', 'updated_at')
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Streak Information', {
            'fields': ('user', 'current_streak', 'longest_streak', 'last_workout_date')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """User Settings admin"""

    list_display = ('user', 'workout_reminders', 'pt_alerts', 'weight_reminder', 'promo_emails', 'class_confirmations')
    list_filter = ('workout_reminders', 'pt_alerts', 'weight_reminder', 'promo_emails', 'class_confirmations')
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)
    list_editable = ('workout_reminders', 'pt_alerts', 'weight_reminder', 'promo_emails', 'class_confirmations')

    fieldsets = (
        ('Notification Settings', {
            'fields': ('workout_reminders', 'pt_alerts', 'weight_reminder', 'promo_emails', 'class_confirmations')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Testimonial admin"""

    list_display = ('name', 'initials', 'rating_display', 'member_since', 'membership_plan', 'is_active', 'is_featured', 'display_order')
    list_filter = ('rating', 'is_active', 'is_featured', 'membership_plan')
    search_fields = ('name', 'content', 'member_since')
    list_editable = ('is_active', 'is_featured', 'display_order')
    list_display_links = ('name',)

    fieldsets = (
        ('Author Information', {
            'fields': ('name', 'initials', 'user')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating')
        }),
        ('Member Details', {
            'fields': ('member_since', 'membership_plan')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'display_order')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def rating_display(self, obj):
        return obj.get_star_display()
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'

    actions = ['make_active', 'make_inactive', 'make_featured']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} testimonials marked as active.')
    make_active.short_description = "Mark selected testimonials as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} testimonials marked as inactive.')
    make_inactive.short_description = "Mark selected testimonials as inactive"

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonials marked as featured.')
    make_featured.short_description = "Feature selected testimonials"


# Custom admin site header
admin.site.site_header = "Atomic Gym Administration"
admin.site.site_title = "Atomic Gym Admin Portal"
admin.site.index_title = "Welcome to Atomic Gym Management System"