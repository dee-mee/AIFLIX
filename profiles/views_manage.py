from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Profile
from .forms import ProfileForm

@login_required
def manage_profiles(request):
    """View for managing all user profiles."""
    profiles = request.user.profiles.all()
    
    # Set the from_manage flag in the session
    request.session['from_manage'] = True
    
    context = {
        'profiles': profiles,
        'can_add_more': len(profiles) < 5,  # Max 5 profiles per user
    }
    return render(request, 'profiles/manage_profiles.html', context)

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_form.html'
    
    def get_success_url(self):
        # Return to manage page after edit
        return reverse('profiles:manage')
    
    def get_queryset(self):
        # Only allow users to edit their own profiles
        return Profile.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['from_manage'] = True  # Indicate we're coming from manage page
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('profiles:manage')

class DeleteProfileView(LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = 'profiles/profile_confirm_delete.html'
    
    def get_success_url(self):
        # Return to manage page after delete
        return reverse('profiles:manage')
    
    def get_queryset(self):
        # Only allow users to delete their own profiles
        return Profile.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        # Clear the profile from session if it's the current one
        profile = self.get_object()
        if 'profile_id' in request.session and str(profile.id) == request.session['profile_id']:
            for key in ['profile_id', 'profile_name', 'profile_avatar']:
                if key in request.session:
                    del request.session[key]
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Profile deleted successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['from_manage'] = True  # Indicate we're coming from manage page
        return context

@login_required
def set_default_profile(request, profile_id):
    """Set a profile as the default for the user."""
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    
    # Only proceed if this is not already the default
    if request.user.default_profile != profile:
        request.user.default_profile = profile
        request.user.save()
        messages.success(request, f'"{profile.name}" is now your default profile.')
    else:
        messages.info(request, f'"{profile.name}" is already your default profile.')
    
    # Redirect back to the previous page or manage profiles
    next_url = request.META.get('HTTP_REFERER')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return HttpResponseRedirect(next_url)
    return redirect('profiles:manage')
