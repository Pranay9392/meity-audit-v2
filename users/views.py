# Project: meity_audit_portal
# App: users
# File: users/views.py
# Description: Handles user authentication (registration, login, logout) and dashboard routing.

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib import messages

def register_request(request):
    """
    Handles user registration.
    If POST request, validates and saves new user.
    If GET request, displays registration form.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately after registration
            messages.success(request, "Registration successful. You are now logged in!")
            return redirect("dashboard") # Redirect to dashboard after successful registration
        else:
            # Add form errors to messages for display
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    form = CustomUserCreationForm()
    return render(request, "users/register.html", {"register_form": form})

def login_request(request):
    """
    Handles user login.
    If POST request, authenticates user.
    If GET request, displays login form.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("dashboard") # Redirect to dashboard after successful login
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "users/login.html", {"login_form": form})

@login_required # Requires user to be logged in to access this view
def logout_request(request):
    """
    Logs out the current user.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login") # Redirect to login page after logout

@login_required
def dashboard_view(request):
    """
    Displays the appropriate dashboard based on the user's role.
    """
    if request.user.is_csp:
        return render(request, "users/dashboard_csp.html")
    elif request.user.is_meity_reviewer:
        return render(request, "users/dashboard_meity_reviewer.html")
    elif request.user.is_stqc_auditor:
        return render(request, "users/dashboard_stqc_auditor.html")
    elif request.user.is_scientist_f:
        return render(request, "users/dashboard_scientist_f.html")
    else:
        # Fallback or error page for undefined roles
        messages.error(request, "Your role is not recognized. Please contact support.")
        logout(request) # Log out user with unrecognized role for security
        return redirect("login")
