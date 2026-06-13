from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    """Inline profile editing within User admin"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Account Type', {
            'fields': ('account_type',)
        }),
        ('Personal Info', {
            'fields': ('bio', 'avatar', 'location', 'birth_date', 'phone')
        }),
        ('Social Links (Creators)', {
            'fields': ('website', 'social_instagram', 'social_twitter', 'social_youtube'),
            'classes': ('collapse',)
        }),
        ('Preferences (Fans)', {
            'fields': ('favorite_genres',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with profile integration"""

    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    list_editable = ('is_active',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )

    inlines = [ProfileInline]

    def get_phone(self, obj):
        return obj.phone or '-'
    get_phone.short_description = 'Phone Number'

    actions = ['activate_users', 'deactivate_users', 'make_staff']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} users were granted staff privileges.')
    make_staff.short_description = "Grant staff privileges"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Standalone Profile admin"""

    list_display = ('user', 'account_type', 'location', 'is_creator_badge', 'created_at')
    list_filter = ('account_type', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'location', 'bio')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Account Type', {
            'fields': ('account_type',)
        }),
        ('Profile Details', {
            'fields': ('bio', 'avatar', 'location', 'birth_date', 'phone')
        }),
        ('Creator Information', {
            'fields': ('website', 'social_instagram', 'social_twitter', 'social_youtube'),
            'classes': ('collapse',),
            'description': 'These fields are only visible for Creator accounts'
        }),
        ('Fan Preferences', {
            'fields': ('favorite_genres',),
            'classes': ('collapse',),
            'description': 'These fields are only visible for Fan accounts'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_creator_badge(self, obj):
        if obj.is_creator:
            return '✓ Creator'
        return 'Fan'
    is_creator_badge.short_description = 'Role'
    is_creator_badge.admin_order_field = 'account_type'