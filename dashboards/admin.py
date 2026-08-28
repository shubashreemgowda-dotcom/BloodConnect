from django.contrib import admin

from .models import (
    DonorProfile,
    BloodRequest,
    SOSAlert,
    BloodBankStock,
    BloodShortageAlert,
    DonationDrive,
)


admin.site.register(DonorProfile)

admin.site.register(BloodRequest)

admin.site.register(SOSAlert)

admin.site.register(BloodBankStock)

admin.site.register(BloodShortageAlert)

admin.site.register(DonationDrive)