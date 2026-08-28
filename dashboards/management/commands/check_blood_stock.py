from django.core.management.base import BaseCommand
from django.db.models import Sum

from dashboards.models import (
    BloodBankStock,
    BloodRequest,
    BloodShortageAlert,
)


class Command(BaseCommand):
    help = "Check blood bank stock against active blood demand."

    LOW_STOCK_THRESHOLD = 5

    def handle(self, *args, **options):
        stocks = BloodBankStock.objects.all().order_by(
            "blood_bank_name",
            "blood_group"
        )

        if not stocks.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No blood bank stock records found."
                )
            )
            return

        demand = BloodRequest.objects.filter(
            status="active"
        ).values(
            "blood_group"
        ).annotate(
            total_required=Sum("units_required")
        )

        demand_map = {
            item["blood_group"]: item["total_required"]
            for item in demand
        }

        processed_groups = set()

        for stock in stocks:
            required = demand_map.get(
                stock.blood_group,
                0
            )

            available = stock.units_available

            shortage = max(
                required - available,
                0
            )

            processed_groups.add(
                (stock.blood_group, stock.city)
            )

            if shortage > 0:

                alert, created = (
                    BloodShortageAlert.objects.update_or_create(
                        blood_group=stock.blood_group,
                        city=stock.city,
                        status="active",
                        defaults={
                            "required_units": required,
                            "available_units": available,
                            "shortage_units": shortage,
                        }
                    )
                )

                action = (
                    "CREATED"
                    if created
                    else "UPDATED"
                )

                self.stdout.write(
                    self.style.ERROR(
                        f"{action} SHORTAGE: "
                        f"{stock.blood_bank_name} - "
                        f"{stock.blood_group} | "
                        f"Required: {required} | "
                        f"Available: {available} | "
                        f"Shortage: {shortage} units"
                    )
                )

            elif available <= self.LOW_STOCK_THRESHOLD:

                self.stdout.write(
                    self.style.WARNING(
                        f"LOW STOCK: "
                        f"{stock.blood_bank_name} - "
                        f"{stock.blood_group} | "
                        f"Available: {available} units"
                    )
                )

            else:

                self.stdout.write(
                    f"OK: "
                    f"{stock.blood_bank_name} - "
                    f"{stock.blood_group} | "
                    f"Required: {required} | "
                    f"Available: {available}"
                )

        active_alerts = BloodShortageAlert.objects.filter(
            status="active"
        )

        for alert in active_alerts:

            if (
                alert.blood_group,
                alert.city
            ) not in processed_groups:
                continue

            required = demand_map.get(
                alert.blood_group,
                0
            )

            stock_total = sum(
                stock.units_available
                for stock in stocks
                if (
                    stock.blood_group
                    == alert.blood_group
                    and stock.city
                    == alert.city
                )
            )

            if stock_total >= required:

                alert.status = "resolved"
                alert.required_units = required
                alert.available_units = stock_total
                alert.shortage_units = 0
                alert.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"RESOLVED: "
                        f"{alert.blood_group} shortage "
                        f"in {alert.city}."
                    )
                )