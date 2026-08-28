from math import radians, sin, cos, sqrt, atan2

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Case, When, IntegerField
from django.utils import timezone

from .forms import DonorProfileForm, BloodRequestForm

from .models import (
    DonorProfile,
    BloodRequest,
    SOSAlert,
    BloodBankStock,
    BloodShortageAlert,
    DonationDrive,
)


# =====================================================
# HOME
# =====================================================

def home(request):
    return render(request, "dashboards/home.html")

# =====================================================
# DISTANCE CALCULATION
# =====================================================

def calculate_distance(lat1, lon1, lat2, lon2):

    if (
        lat1 is None
        or lon1 is None
        or lat2 is None
        or lon2 is None
    ):
        return None

    R = 6371

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


# =====================================================
# DONOR DASHBOARD
# =====================================================

@login_required
def donor_dashboard(request):

    donor_profile = DonorProfile.objects.filter(
        user=request.user
    ).first()

    matching_requests = []

    if donor_profile:

        requests = (
            BloodRequest.objects.filter(
                status="active",
                hospital_verified=True,
            )
            .annotate(
                urgency_priority=Case(
                    When(
                        urgency="emergency",
                        then=0
                    ),
                    When(
                        urgency="critical",
                        then=0
                    ),
                    When(
                        urgency="urgent",
                        then=1
                    ),
                    default=2,
                    output_field=IntegerField(),
                )
            )
            .order_by(
                "urgency_priority",
                "-created_at",
            )
        )

        for blood_request in requests:

            # Blood group must match
            if (
                blood_request.blood_group
                != donor_profile.blood_group
            ):
                continue

            distance = calculate_distance(
                donor_profile.latitude,
                donor_profile.longitude,
                blood_request.latitude,
                blood_request.longitude,
            )

            if distance is None:
                continue

            matching_requests.append({
                "request": blood_request,
                "distance": round(distance, 2),
            })

    sos_alerts = (
        SOSAlert.objects.filter(
            donor=donor_profile
        )
        .select_related("blood_request")
        .order_by("-id")
        if donor_profile
        else []
    )

    return render(
        request,
        "dashboards/donor.html",
        {
            "donor_profile": donor_profile,
            "matching_requests": matching_requests,
            "sos_alerts": sos_alerts,
        },
    )


# =====================================================
# DONOR PROFILE
# =====================================================

@login_required
def donor_profile(request):

    profile = DonorProfile.objects.filter(
        user=request.user
    ).first()

    if request.method == "POST":

        form = DonorProfileForm(
            request.POST,
            instance=profile,
        )

        if form.is_valid():

            donor = form.save(
                commit=False
            )

            donor.user = request.user
            donor.save()

            return redirect(
                "donor_profile"
            )

    else:

        form = DonorProfileForm(
            instance=profile
        )

    return render(
        request,
        "dashboards/profile.html",
        {
            "form": form,
            "profile": profile,
        },
    )


# =====================================================
# SEEKER DASHBOARD
# =====================================================

@login_required
def seeker_dashboard(request):

    blood_requests = (
        BloodRequest.objects.filter(
            user=request.user
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "dashboards/seeker.html",
        {
            "blood_requests": blood_requests,
        },
    )


# =====================================================
# BLOOD REQUEST
# =====================================================

@login_required
def blood_request(request):

    if request.method == "POST":

        form = BloodRequestForm(
            request.POST
        )

        if form.is_valid():

            blood_request_obj = form.save(
                commit=False
            )

            # IMPORTANT:
            # Your BloodRequest model uses "user"
            blood_request_obj.user = request.user

            blood_request_obj.save()

            return redirect(
                "seeker_dashboard"
            )

    else:

        form = BloodRequestForm()

    return render(
        request,
        "dashboards/blood_request.html",
        {
            "form": form,
        },
    )


# =====================================================
# CREATE BLOOD REQUEST
# =====================================================

@login_required
def create_blood_request(request):

    return blood_request(request)


# =====================================================
# HOSPITAL DASHBOARD
# =====================================================

@login_required
def hospital_dashboard(request):

    # =================================================
    # HANDLE HOSPITAL ACTIONS
    # =================================================

    if request.method == "POST":

        request_id = request.POST.get(
            "request_id"
        )

        action = request.POST.get(
            "action"
        )

        blood_request_obj = (
            BloodRequest.objects.filter(
                id=request_id
            ).first()
        )

        if blood_request_obj:

            # =========================================
            # VERIFY REQUEST
            # =========================================

            if action == "verify":

                blood_request_obj.hospital_verified = True
                blood_request_obj.status = "active"

                blood_request_obj.save()


            # =========================================
            # APPROVE SOS
            # =========================================

            elif action == "approve_sos":

                blood_request_obj.hospital_verified = True
                blood_request_obj.sos_approved = True
                blood_request_obj.status = "active"
                blood_request_obj.current_wave = 1

                blood_request_obj.save()

                create_sos_wave(
                    request,
                    blood_request_obj.id
                )


            # =========================================
            # COMPLETE REQUEST
            # =========================================

            elif action == "complete":

                blood_request_obj.status = "fulfilled"

                blood_request_obj.save()


        return redirect(
            "hospital_dashboard"
        )


    # =================================================
    # ALL REQUESTS BELONGING TO THIS HOSPITAL
    # =================================================

    blood_requests = (
        BloodRequest.objects.filter(
            user=request.user
        )
        .order_by("-created_at")
    )


    # =================================================
    # PENDING REQUESTS
    # =================================================

    pending_requests = (
        blood_requests.filter(
            hospital_verified=False
        )
        .order_by("-created_at")
    )


    # =================================================
    # VERIFIED ACTIVE REQUESTS
    # =================================================

    verified_requests = (
        blood_requests.filter(
            hospital_verified=True,
            status="active"
        )
        .order_by("-created_at")
    )


    # =================================================
    # ACTIVE SOS REQUESTS
    # =================================================

    sos_requests = (
        blood_requests.filter(
            hospital_verified=True,
            sos_approved=True,
            status="active"
        )
        .order_by("-created_at")
    )


    # =================================================
    # COUNTS
    # =================================================

    active_requests = blood_requests.filter(
        status="active"
    ).count()

    emergency_requests = blood_requests.filter(
        urgency="emergency",
        status="active"
    ).count()

    urgent_requests = blood_requests.filter(
        urgency="urgent",
        status="active"
    ).count()


    # =================================================
    # SOS ALERTS
    # =================================================

    sos_alerts = (
        SOSAlert.objects.filter(
            blood_request__user=request.user
        )
        .select_related(
            "blood_request",
            "donor",
        )
        .order_by("-id")
    )


    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "dashboards/hospital.html",
        {
            "blood_requests": blood_requests,

            "pending_requests": pending_requests,

            "verified_requests": verified_requests,

            "sos_requests": sos_requests,

            "active_requests": active_requests,

            "emergency_requests": emergency_requests,

            "urgent_requests": urgent_requests,

            "critical_requests": emergency_requests,

            "sos_alerts": sos_alerts,
        },
    )


# =====================================================
# CREATE SOS WAVE
# =====================================================

@login_required
def create_sos_wave(
    request,
    request_id
):

    blood_request_obj = (
        BloodRequest.objects.filter(
            id=request_id,
            user=request.user,
        )
        .first()
    )

    if not blood_request_obj:

        return redirect(
            "hospital_dashboard"
        )


    donors = (
        DonorProfile.objects.filter(
            is_available=True
        )
        .exclude(
            latitude__isnull=True
        )
        .exclude(
            longitude__isnull=True
        )
    )


    nearby_donors = []


    for donor in donors:

        # Match blood group
        if (
            donor.blood_group
            != blood_request_obj.blood_group
        ):
            continue


        distance = calculate_distance(
            blood_request_obj.latitude,
            blood_request_obj.longitude,
            donor.latitude,
            donor.longitude,
        )


        if distance is None:
            continue


        # WAVE 1 = 0-2 KM
        if distance <= 2:

            nearby_donors.append({
                "donor": donor,
                "distance": distance,
            })


    nearby_donors.sort(
        key=lambda item: item["distance"]
    )


    # =================================================
    # CREATE ALERTS
    # =================================================

    for item in nearby_donors:

        SOSAlert.objects.get_or_create(
            blood_request=blood_request_obj,

            donor=item["donor"],

            wave=1,

            defaults={
                "distance_km": item["distance"],
                "status": "active",
            },
        )


    blood_request_obj.current_wave = 1
    blood_request_obj.sos_approved = True

    blood_request_obj.save(
        update_fields=[
            "current_wave",
            "sos_approved",
        ]
    )


    return redirect(
        "hospital_dashboard"
    )


# =====================================================
# MOVE TO NEXT SOS WAVE
# =====================================================

@login_required
def move_to_next_wave(
    request,
    request_id
):

    blood_request_obj = (
        BloodRequest.objects.filter(
            id=request_id,
            user=request.user,
        )
        .first()
    )


    if not blood_request_obj:

        return redirect(
            "hospital_dashboard"
        )


    next_wave = (
        blood_request_obj.current_wave
        + 1
    )


    # Maximum 5 waves
    if next_wave > 5:

        return redirect(
            "hospital_dashboard"
        )


    # =================================================
    # DISTANCE
    # =================================================

    if next_wave == 1:

        min_distance = 0
        max_distance = 2

    elif next_wave == 2:

        min_distance = 2
        max_distance = 4

    elif next_wave == 3:

        min_distance = 4
        max_distance = 6

    elif next_wave == 4:

        min_distance = 6
        max_distance = 10

    else:

        min_distance = 10
        max_distance = 20


    donors = (
        DonorProfile.objects.filter(
            is_available=True
        )
        .exclude(
            latitude__isnull=True
        )
        .exclude(
            longitude__isnull=True
        )
    )


    for donor in donors:

        if (
            donor.blood_group
            != blood_request_obj.blood_group
        ):
            continue


        distance = calculate_distance(
            blood_request_obj.latitude,
            blood_request_obj.longitude,
            donor.latitude,
            donor.longitude,
        )


        if distance is None:
            continue


        if (
            distance > min_distance
            and distance <= max_distance
        ):

            SOSAlert.objects.get_or_create(

                blood_request=blood_request_obj,

                donor=donor,

                wave=next_wave,

                defaults={
                    "distance_km": distance,
                    "status": "active",
                },
            )


    blood_request_obj.current_wave = next_wave

    blood_request_obj.save(
        update_fields=[
            "current_wave"
        ]
    )


    return redirect(
        "hospital_dashboard"
    )


# =====================================================
# RESPOND TO SOS
# =====================================================

@login_required
def respond_to_sos(
    request,
    alert_id
):

    if request.method != "POST":

        return redirect(
            "donor_dashboard"
        )


    donor_profile = (
        DonorProfile.objects.filter(
            user=request.user
        )
        .first()
    )


    if not donor_profile:

        return redirect(
            "donor_profile"
        )


    alert = (
        SOSAlert.objects.filter(
            id=alert_id,
            donor=donor_profile,
        )
        .select_related(
            "blood_request"
        )
        .first()
    )


    if not alert:

        return redirect(
            "donor_dashboard"
        )


    # Only active alerts can be answered
    if alert.status != "active":

        return redirect(
            "donor_dashboard"
        )


    # Mark donor as responded
    alert.status = "responded"

    alert.responded_at = timezone.now()

    alert.save(
        update_fields=[
            "status",
            "responded_at",
        ]
    )


    # Fulfil request
    blood_request_obj = alert.blood_request

    blood_request_obj.status = "fulfilled"

    blood_request_obj.save(
        update_fields=[
            "status"
        ]
    )


    # Cancel other active alerts
    SOSAlert.objects.filter(
        blood_request=blood_request_obj,
        status="active",
    ).exclude(
        id=alert.id
    ).update(
        status="cancelled"
    )


    return redirect(
        "donor_dashboard"
    )


# =====================================================
# RESPOND TO BLOOD REQUEST
# =====================================================

@login_required
def respond_to_blood_request(request):

    if request.method != "POST":

        return redirect(
            "donor_dashboard"
        )


    request_id = request.POST.get(
        "request_id"
    )


    blood_request_obj = (
        BloodRequest.objects.filter(
            id=request_id,
            status="active",
        )
        .first()
    )


    if not blood_request_obj:

        return redirect(
            "donor_dashboard"
        )


    donor_profile = (
        DonorProfile.objects.filter(
            user=request.user
        )
        .first()
    )


    if not donor_profile:

        return redirect(
            "donor_profile"
        )


    alert = (
        SOSAlert.objects.filter(
            blood_request=blood_request_obj,
            donor=donor_profile,
            status="active",
        )
        .order_by("-id")
        .first()
    )


    if alert:

        alert.status = "responded"

        alert.responded_at = timezone.now()

        alert.save(
            update_fields=[
                "status",
                "responded_at",
            ]
        )


    return redirect(
        "donor_dashboard"
    )


# =====================================================
# COMPLETE BLOOD REQUEST
# =====================================================

@login_required
def complete_blood_request(
    request,
    request_id
):

    blood_request_obj = (
        BloodRequest.objects.filter(
            id=request_id,
            user=request.user,
        )
        .first()
    )


    if not blood_request_obj:

        return redirect(
            "hospital_dashboard"
        )


    blood_request_obj.status = "fulfilled"

    blood_request_obj.save(
        update_fields=[
            "status"
        ]
    )


    # Cancel remaining active alerts
    SOSAlert.objects.filter(
        blood_request=blood_request_obj,
        status="active",
    ).update(
        status="cancelled"
    )


    return redirect(
        "hospital_dashboard"
    )


# =====================================================
# BLOOD BANK DASHBOARD
# =====================================================

@login_required
def blood_bank_dashboard(request):

    stocks = (
        BloodBankStock.objects.filter(
            blood_bank=request.user
        )
        .order_by("blood_group")
    )


    shortage_alerts = (
        BloodShortageAlert.objects.filter(
            blood_bank=request.user
        )
        .order_by("-created_at")
    )


    return render(
        request,
        "dashboards/blood_bank.html",
        {
            "stocks": stocks,
            "shortage_alerts": shortage_alerts,
        },
    )


# =====================================================
# COLLEGE DASHBOARD
# =====================================================

@login_required
def college_dashboard(request):

    college_donors = (
        DonorProfile.objects.filter(
            college=request.user
        )
        .select_related("user")
        .order_by(
            "-is_available",
            "user__username",
        )
    )


    registered_donors = (
        college_donors.count()
    )


    available_donors = (
        college_donors
        .filter(
            is_available=True
        )
        .count()
    )


    donation_drives = (
        DonationDrive.objects.filter(
            college=request.user
        )
        .order_by(
            "-date",
            "-id",
        )
    )


    donation_drive_count = (
        donation_drives.count()
    )


    # =================================================
    # CREATE DONATION DRIVE
    # =================================================

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )


        if action == "create_drive":

            title = request.POST.get(
                "title"
            )

            date = request.POST.get(
                "date"
            )

            expected_donors = request.POST.get(
                "expected_donors"
            )

            location = request.POST.get(
                "location"
            )


            if (
                title
                and date
                and location
            ):

                DonationDrive.objects.create(

                    college=request.user,

                    title=title,

                    date=date,

                    expected_donors=(
                        expected_donors or 0
                    ),

                    location=location,

                    status="planned",
                )


            return redirect(
                "college_dashboard"
            )


    return render(
        request,
        "dashboards/college.html",
        {
            "college_donors": college_donors,

            "registered_donors":
                registered_donors,

            "available_donors":
                available_donors,

            "donation_drives":
                donation_drives,

            "donation_drive_count":
                donation_drive_count,
        },
    )
    # =====================================================
# BLOOD REQUEST DETAIL
# =====================================================

@login_required
def blood_request_detail(request, request_id):

    blood_request_obj = (
        BloodRequest.objects
        .filter(
            id=request_id,
            user=request.user,
        )
        .first()
    )

    if not blood_request_obj:
        return redirect("hospital_dashboard")

    sos_alerts = (
        SOSAlert.objects
        .filter(
            blood_request=blood_request_obj
        )
        .select_related("donor", "donor__user")
        .order_by("wave", "distance_km")
    )

    return render(
        request,
        "dashboards/blood_request_detail.html",
        {
            "blood_request": blood_request_obj,
            "sos_alerts": sos_alerts,
        },
    )
    # =====================================================
# CANCEL SOS
# =====================================================

@login_required
def cancel_sos(request, request_id):

    if request.method != "POST":
        return redirect("hospital_dashboard")

    blood_request_obj = (
        BloodRequest.objects.filter(
            id=request_id,
            user=request.user,
        )
        .first()
    )

    if not blood_request_obj:
        return redirect("hospital_dashboard")

    # Stop SOS for this blood request
    blood_request_obj.sos_approved = False
    blood_request_obj.save(
        update_fields=["sos_approved"]
    )

    # Cancel all active donor alerts
    SOSAlert.objects.filter(
        blood_request=blood_request_obj,
        status="active",
    ).update(
        status="cancelled"
    )

    return redirect("hospital_dashboard")
    # =====================================================
# AUTO ADVANCE SOS
# =====================================================

@login_required
def auto_advance_sos(request, request_id):

    blood_request_obj = (
        BloodRequest.objects.filter(
            id=request_id,
            user=request.user,
        )
        .first()
    )

    if not blood_request_obj:
        return redirect("hospital_dashboard")

    # Only active SOS requests can advance
    if (
        blood_request_obj.status != "active"
        or not blood_request_obj.sos_approved
    ):
        return redirect("hospital_dashboard")

    # Check whether there are still active donor alerts
    active_alerts = SOSAlert.objects.filter(
        blood_request=blood_request_obj,
        status="active",
    ).exists()

    # If someone is already responding, don't advance
    if active_alerts:
        return redirect("hospital_dashboard")

    # Move to the next wave
    if blood_request_obj.current_wave < 5:
        return move_to_next_wave(
            request,
            request_id
        )

    return redirect("hospital_dashboard")