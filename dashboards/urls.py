from django.urls import path

from . import views


urlpatterns = [

    # ============================================================
    # GENERAL
    # ============================================================

    path(
        "",
        views.home,
        name="home"
    ),

    # ============================================================
    # DONOR
    # ============================================================

    path(
        "donor/",
        views.donor_dashboard,
        name="donor_dashboard"
    ),

    path(
        "donor/profile/",
        views.donor_profile,
        name="donor_profile"
    ),

    path(
        "donor/sos/respond/<int:alert_id>/",
        views.respond_to_sos,
        name="respond_to_sos"
    ),

    # ============================================================
    # SEEKER
    # ============================================================

    path(
        "seeker/",
        views.seeker_dashboard,
        name="seeker_dashboard"
    ),

    # ============================================================
    # HOSPITAL
    # ============================================================

    path(
        "hospital/",
        views.hospital_dashboard,
        name="hospital_dashboard"
    ),

    # ============================================================
    # BLOOD REQUEST
    # ============================================================

    path(
        "hospital/blood-request/create/",
        views.create_blood_request,
        name="create_blood_request"
    ),

    path(
        "hospital/blood-request/<int:blood_request_id>/",
        views.blood_request_detail,
        name="blood_request_detail"
    ),

    # ============================================================
    # SOS
    # ============================================================

    path(
        "hospital/sos/<int:blood_request_id>/",
        views.create_sos_wave,
        name="create_sos_wave"
    ),

    path(
        "hospital/sos/<int:blood_request_id>/next-wave/",
        views.move_to_next_wave,
        name="move_to_next_wave"
    ),

    path(
        "hospital/sos/<int:blood_request_id>/cancel/",
        views.cancel_sos,
        name="cancel_sos"
    ),

    path(
        "hospital/blood-request/<int:blood_request_id>/complete/",
        views.complete_blood_request,
        name="complete_blood_request"
    ),

    # ============================================================
    # AUTOMATIC SOS WAVE ADVANCEMENT
    #
    # IMPORTANT:
    # There is NO <int:blood_request_id> here.
    #
    # JavaScript calls this URL directly:
    # /dashboards/hospital/sos/auto-advance/
    # ============================================================

    path(
        "hospital/sos/auto-advance/",
        views.auto_advance_sos,
        name="auto_advance_sos"
    ),
]