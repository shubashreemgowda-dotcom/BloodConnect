from django.db import models
from accounts.models import User


# =====================================================
# DONOR PROFILE
# =====================================================

class DonorProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    college = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_donors",
        limit_choices_to={"role": "college"}
    )

    blood_group = models.CharField(
        max_length=5
    )

    phone = models.CharField(
        max_length=15
    )

    city = models.CharField(
        max_length=100
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    is_available = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.user.username


# =====================================================
# BLOOD REQUEST
# =====================================================

class BloodRequest(models.Model):

    URGENCY_CHOICES = [
        ("normal", "Normal"),
        ("urgent", "Urgent"),
        ("emergency", "Emergency"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Verification"),
        ("active", "Active"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    blood_group = models.CharField(
        max_length=5
    )

    units_required = models.PositiveIntegerField()

    hospital_name = models.CharField(
        max_length=200
    )

    city = models.CharField(
        max_length=100
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default="normal"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    hospital_verified = models.BooleanField(
        default=False
    )

    sos_approved = models.BooleanField(
        default=False
    )

    current_wave = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.blood_group} - {self.units_required} units"


# =====================================================
# SOS ALERT
# =====================================================

class SOSAlert(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("responded", "Responded"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE
    )

    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE
    )

    distance_km = models.FloatField()

    wave = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    responded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"SOS - {self.blood_request.blood_group} - "
            f"{self.donor.user.username}"
        )


# =====================================================
# BLOOD BANK STOCK
# =====================================================

class BloodBankStock(models.Model):

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    blood_bank = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blood_bank_stocks",
        limit_choices_to={"role": "blood_bank"},
        null=True,
        blank=True
    )

    blood_bank_name = models.CharField(
        max_length=200
    )

    city = models.CharField(
        max_length=100
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )

    units_available = models.PositiveIntegerField(
        default=0
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.blood_bank_name} - "
            f"{self.blood_group} - "
            f"{self.units_available} units"
        )


# =====================================================
# BLOOD SHORTAGE ALERT
# =====================================================

class BloodShortageAlert(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("resolved", "Resolved"),
    ]

    blood_group = models.CharField(
        max_length=5
    )

    city = models.CharField(
        max_length=100
    )

    required_units = models.PositiveIntegerField()

    available_units = models.PositiveIntegerField()

    shortage_units = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.blood_group} shortage - "
            f"{self.shortage_units} units"
        )


# =====================================================
# DONATION DRIVE
# =====================================================

class DonationDrive(models.Model):

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    college = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="donation_drives",
        limit_choices_to={"role": "college"}
    )

    title = models.CharField(
        max_length=200
    )

    date = models.DateField()

    location = models.CharField(
        max_length=200
    )

    expected_donors = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title