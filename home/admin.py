from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import ContactMessage, GymMembership

User = get_user_model()

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_editable = ('is_read',)

@admin.register(GymMembership)
class GymMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_plan', 'status', 'start_date', 'end_date')
    list_filter = ('membership_plan', 'status', 'fitness_goal')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_editable = ('status',)