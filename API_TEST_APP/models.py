from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

from django.db import models, transaction, IntegrityError
from django.utils import timezone


class ShipmentID_Models(models.Model):
    shipment_id = models.CharField(max_length=20, unique=True)
    tocken = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "WHR_UNIQUE_SHIPMENT_ID"
        ordering = ["id"]

    @staticmethod
    def generate_shipment_id():
        today = timezone.now()
        year = today.strftime("%y")   # last 2 digits of year
        month = today.strftime("%m")  # 2-digit month

        prefix = f"INO{year}{month}"

        # Only check current month's records
        last_record = (
            ShipmentID_Models.objects
            .filter(shipment_id__startswith=prefix)   # filter by this month's prefix
            .select_for_update(skip_locked=True)
            .order_by("-tocken")
            .first()
        )

        if last_record:
            next_tocken = last_record.tocken + 1
        else:
            next_tocken = 1

        tocken_str = str(next_tocken).zfill(2)  # 01, 02, 03...
        shipment_code = f"{prefix}{tocken_str}"
        return shipment_code, next_tocken



