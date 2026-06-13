from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm
from .models import Profile
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
    success_url = reverse_lazy('accounts:profile')

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
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        context['title'] = 'Dashboard'

        # Add account type specific context
        if context['profile'].is_creator:
            context['creator_specific_data'] = self.get_creator_data()
        else:
            context['fan_specific_data'] = self.get_fan_data()

        return context

    def get_creator_data(self):
        # Add creator-specific data here
        # For example: number of posts, followers, etc.
        return {
            'total_posts': 0,  # Replace with actual query
            'total_followers': 0,  # Replace with actual query
        }

    def get_fan_data(self):
        # Add fan-specific data here
        # For example: followed creators, liked content, etc.
        return {
            'following_count': 0,  # Replace with actual query
            'liked_content_count': 0,  # Replace with actual query
        }

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        # Return the profile of the logged-in user
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to update profile. Please correct the errors.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Profile'
        return context

class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_detail.html'
    login_url = 'accounts:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        if user_id:
            context['profile_user'] = User.objects.get(id=user_id)
        else:
            context['profile_user'] = self.request.user
        context['title'] = f"{context['profile_user'].username}'s Profile"
        return context