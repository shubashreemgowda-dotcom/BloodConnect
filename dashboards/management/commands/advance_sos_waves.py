from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from dashboards.models import BloodRequest, SOSAlert
from dashboards.views import move_to_next_wave


class Command(BaseCommand):
    help = "Advance SOS requests to the next donor wave when the current wave times out."

    WAITING_MINUTES = 5

    def handle(self, *args, **options):

        cutoff_time = timezone.now() - timedelta(
            minutes=self.WAITING_MINUTES
        )

        requests = BloodRequest.objects.filter(
            status='active',
            sos_approved=True
        )

        for blood_request in requests:

            current_wave_alerts = SOSAlert.objects.filter(
                blood_request=blood_request,
                wave=blood_request.current_wave
            )

            if not current_wave_alerts.exists():
                continue

            if current_wave_alerts.filter(
                status='responded'
            ).exists():
                continue

            active_alerts = current_wave_alerts.filter(
                status='active'
            )

            if active_alerts.filter(
                created_at__gt=cutoff_time
            ).exists():
                continue

            # Current wave has timed out.
            # Cancel unanswered alerts before moving
            # to the next wave.
            active_alerts.update(
                status='cancelled'
            )

            move_to_next_wave(blood_request)

            blood_request.refresh_from_db()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Request {blood_request.id} "
                    f"advanced to wave "
                    f"{blood_request.current_wave}."
                )
            )