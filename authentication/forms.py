from django import forms

from accounts.models import User


# =====================================================
# REGISTRATION FORM
# =====================================================

class RegistrationForm(forms.ModelForm):

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Create a password",
                "class": "form-control",
            }
        )
    )

    class Meta:

        model = User

        fields = [
            "username",
            "email",
            "password",
            "role",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "placeholder": "Enter username",
                    "class": "form-control",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter email",
                    "class": "form-control",
                }
            ),

            "role": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

        labels = {
            "username": "Username",
            "email": "Email",
            "role": "Account Type",
        }

    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                "This username is already registered."
            )

        return username