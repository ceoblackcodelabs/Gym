from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm, MembershipRegistrationForm
from .models import ContactMessage, Testimonial

User = get_user_model()

class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactForm()
        context['membership_form'] = MembershipRegistrationForm()
        context['testimonials'] = Testimonial.objects.filter(is_active=True).order_by('display_order', '-created_at')
        return context


class ContactAPIView(View):
    """API endpoint for contact form submissions"""

    def post(self, request):
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': '✓ Message sent! We\'ll get back to you within 24 hours.'
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
            login(request, user)

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
    """Check if a user exists by email"""

    def get(self, request):
        email = request.GET.get('email', '')
        if email and User.objects.filter(email=email).exists():
            return JsonResponse({'exists': True, 'message': 'Email already registered'})
        return JsonResponse({'exists': False})


