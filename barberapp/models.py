from django.db import models
from django.utils import timezone

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("cancelled", "Cancelled"),
        ("done", "Done"),
    ]

    phone = models.CharField(max_length=20, db_index=True)  # 998XXXXXXXXX
    scheduled_at = models.DateTimeField(db_index=True)      # kelish vaqti

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    created_at = models.DateTimeField(default=timezone.now)

    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    reminder_attempts = models.PositiveIntegerField(default=0)
    last_reminder_error = models.TextField(null=True, blank=True)

    eskiz_request_id = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.phone} @ {self.scheduled_at}"
