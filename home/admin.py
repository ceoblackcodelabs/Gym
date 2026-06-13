from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import ContactMessage, GymMembership, Testimonial

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

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating_display', 'member_since', 'membership_plan', 'is_active', 'is_featured', 'display_order')
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

    actions = ['make_active', 'make_inactive', 'make_featured']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected testimonials as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected testimonials as inactive"

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Feature selected testimonials"