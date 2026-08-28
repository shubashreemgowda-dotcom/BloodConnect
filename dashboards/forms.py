from django import forms

from .models import (
    DonorProfile,
    BloodRequest,
)


# =====================================================
# BLOOD GROUP CHOICES
# =====================================================

BLOOD_GROUP_CHOICES = [
    ("", "Select Blood Group"),
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
    ("O+", "O+"),
    ("O-", "O-"),
]


# =====================================================
# DONOR PROFILE FORM
# =====================================================

class DonorProfileForm(forms.ModelForm):

    class Meta:

        model = DonorProfile

        fields = [
            "blood_group",
            "phone",
            "city",
            "college",
            "latitude",
            "longitude",
            "is_available",
        ]

        widgets = {

            "blood_group": forms.Select(
                choices=BLOOD_GROUP_CHOICES,
                attrs={
                    "class": "form-control",
                }
            ),

            "college": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Enter phone number",
                    "class": "form-control",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "placeholder": "Enter city",
                    "class": "form-control",
                }
            ),

            "latitude": forms.NumberInput(
                attrs={
                    "step": "any",
                    "placeholder": "Latitude",
                    "class": "form-control",
                }
            ),

            "longitude": forms.NumberInput(
                attrs={
                    "step": "any",
                    "placeholder": "Longitude",
                    "class": "form-control",
                }
            ),

            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "form-check",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["college"].queryset = (
            self.fields["college"]
            .queryset
            .filter(role="college")
            .order_by("username")
        )

        self.fields["college"].label = "College"


# =====================================================
# BLOOD REQUEST FORM
# =====================================================

class BloodRequestForm(forms.ModelForm):

    class Meta:

        model = BloodRequest

        fields = [
            "blood_group",
            "units_required",
            "hospital_name",
            "city",
            "latitude",
            "longitude",
            "urgency",
        ]

        widgets = {

            "blood_group": forms.Select(
                choices=BLOOD_GROUP_CHOICES,
                attrs={
                    "class": "form-control",
                }
            ),

            "units_required": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 20,
                    "class": "form-control",
                }
            ),

            "hospital_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter hospital name",
                    "class": "form-control",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "placeholder": "Enter city",
                    "class": "form-control",
                }
            ),

            "latitude": forms.NumberInput(
                attrs={
                    "step": "any",
                    "placeholder": "Latitude",
                    "class": "form-control",
                }
            ),

            "longitude": forms.NumberInput(
                attrs={
                    "step": "any",
                    "placeholder": "Longitude",
                    "class": "form-control",
                }
            ),

            "urgency": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_units_required(self):

        units = self.cleaned_data["units_required"]

        if units < 1:
            raise forms.ValidationError(
                "Units required must be at least 1."
            )

        if units > 20:
            raise forms.ValidationError(
                "Units required cannot be more than 20."
            )

        return units