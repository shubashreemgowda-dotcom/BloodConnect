from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RegistrationForm


# =====================================================
# TEST AUTHENTICATION
# =====================================================

def test_authentication(request):
    return HttpResponse(
        "BloodConnect Authentication is working!"
    )


# =====================================================
# ROLE SELECTION
# =====================================================

def role_selection(request):
    return render(
        request,
        "authentication/role_selection.html"
    )


# =====================================================
# REGISTER
# =====================================================

def register(request):

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(
                commit=False
            )

            user.set_password(
                form.cleaned_data["password"]
            )

            user.save()

            # After successful registration,
            # take the user to the login page.
            return redirect(
                "/auth/login/"
            )

    else:

        form = RegistrationForm()

    return render(
        request,
        "authentication/register.html",
        {
            "form": form
        }
    )


# =====================================================
# LOGIN
# =====================================================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        )

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            # =========================================
            # ROLE-BASED DASHBOARD REDIRECT
            # =========================================

            if user.role == "donor":

                return redirect(
                    "/dashboards/donor/"
                )

            elif user.role == "seeker":

                return redirect(
                    "/dashboards/seeker/"
                )

            elif user.role == "hospital":

                return redirect(
                    "/dashboards/hospital/"
                )

            elif user.role == "blood_bank":

                return redirect(
                    "/dashboards/blood-bank/"
                )

            elif user.role == "college":

                return redirect(
                    "/dashboards/college/"
                )

            # If a user has no valid role,
            # log them out instead of leaving
            # them on an undefined page.
            logout(request)

            return HttpResponse(
                "User role is not configured."
            )

        return HttpResponse(
            "Invalid username or password"
        )

    return render(
        request,
        "authentication/login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

def user_logout(request):

    logout(request)

    return redirect(
        "/auth/login/"
    )