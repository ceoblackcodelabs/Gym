from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm, MembershipRegistrationForm
from .models import ContactMessage

User = get_user_model()

class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactForm()
        context['membership_form'] = MembershipRegistrationForm()
        return context


class ContactAPIView(View):
    """API endpoint for contact form submissions"""

    def post(self, request):
        form = ContactForm(request.POST)

        if form.is_valid():
            message = form.save()

            # Optional: Send email notification
            try:
                send_mail(
                    subject=f"New Contact Message: {message.subject}",
                    message=f"From: {message.first_name} {message.last_name}\nEmail: {message.email}\nPhone: {message.phone}\n\nMessage:\n{message.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except:
                pass

            return JsonResponse({
                'success': True,
                'message': f'✓ Thanks {message.first_name}! We\'ll get back to you within 24 hours.'
            })

        return JsonResponse({
            'success': False,
            'errors': dict(form.errors)
        }, status=400)


class MembershipRegistrationAPIView(View):
    """API endpoint for membership registration"""

    def post(self, request):
        form = MembershipRegistrationForm(request.POST)

        if form.is_valid():
            user, membership = form.save()

            # Log the user in automatically
            login(request, user)

            # Optional: Send welcome email
            try:
                send_mail(
                    subject="Welcome to Atomic Gym!",
                    message=f"Hi {user.first_name},\n\nWelcome to Atomic Gym! Your {membership.get_membership_plan_display()} membership is now active.\n\nWe're excited to have you on board!\n\nBest regards,\nAtomic Gym Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass

            return JsonResponse({
                'success': True,
                'message': f'✓ Welcome {user.first_name}! Your {membership.get_membership_plan_display()} plan is now active.',
                'redirect_url': '/'
            })

        return JsonResponse({
            'success': False,
            'errors': dict(form.errors)
        }, status=400)


class CheckMemberExistsAPIView(View):
    """Check if a user exists by email (for real-time validation)"""

    def get(self, request):
        email = request.GET.get('email', '')
        if email and User.objects.filter(email=email).exists():
            return JsonResponse({'exists': True, 'message': 'Email already registered'})
        return JsonResponse({'exists': False})