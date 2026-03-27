# barberapp/management/commands/send_reminders.py
import math
from django.core.management.base import BaseCommand
from django.utils import timezone

from barberapp.models import Appointment
from barberapp.eskiz_client import EskizClient

# ✅ ENV YO'Q — shu yerda boshqarasiz
DEFAULT_REMIND_BEFORE_MINUTES = 2

# ✅ Cron/Task kechikishi uchun "grace"
LATE_GRACE_SECONDS = 180   # 3 minut kechiksa ham yubor
EARLY_GRACE_SECONDS = 60   # 1 minut erta yuborishi mumkin


class Command(BaseCommand):
    help = "Send SMS reminders with dynamic date/time (no env)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=DEFAULT_REMIND_BEFORE_MINUTES,
            help="Necha minut oldin SMS yuborilsin (default 2).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="SMS yubormaydi, faqat qaysi appointmentlar tushganini ko'rsatadi.",
        )
        parser.add_argument(
            "--force-id",
            type=int,
            default=None,
            help="Test uchun bitta appointment id ni tekshiradi/yuboradi.",
        )

    def handle(self, *args, **options):
        remind_before = int(options["minutes"])
        dry_run = bool(options["dry_run"])
        force_id = options["force_id"]

        now = timezone.now()

        # ✅ Target: scheduled_at taxminan (now + remind_before)
        target = now + timezone.timedelta(minutes=remind_before)

        # ✅ Robust rejim: end = target + grace, start = now
        # Bu logic script kechiksa ham SMS yuborishni kafolatlaydi.
        end = target + timezone.timedelta(seconds=EARLY_GRACE_SECONDS)
        start = now  # faqat kelajakdagilarni yuboramiz

        client = EskizClient()

        if force_id is not None:
            appt = Appointment.objects.filter(id=force_id).first()
            if not appt:
                self.stdout.write(f"[send_reminders] force-id={force_id} NOT FOUND")
                return

            self.stdout.write(
                f"[send_reminders] FORCE appt_id={appt.id} phone={appt.phone} "
                f"status={appt.status} scheduled_utc={appt.scheduled_at.isoformat()} "
                f"scheduled_local={timezone.localtime(appt.scheduled_at).isoformat()} "
                f"reminder_sent_at={appt.reminder_sent_at}"
            )
            qs = [appt]
        else:
            qs = list(
                Appointment.objects.filter(
                    status="scheduled",
                    reminder_sent_at__isnull=True,
                    scheduled_at__gt=now,
                    scheduled_at__lte=end,             # ✅ target_vaqt + grace gacha hamma kutayotganlarni yuborish
                ).order_by("scheduled_at")
            )

            self.stdout.write(
                f"[send_reminders] now={now.isoformat()} minutes={remind_before} "
                f"target={target.isoformat()} window=[{now.isoformat()} .. {end.isoformat()}] "
                f"matches={len(qs)} dry_run={dry_run}"
            )

        for appt in qs:
            # ✅ cancelled / already sent bo'lsa yubormaymiz (force bo'lsa ham)
            if appt.status != "scheduled":
                self.stdout.write(f"  - SKIP appt_id={appt.id} reason=status={appt.status}")
                continue

            if appt.reminder_sent_at is not None:
                self.stdout.write(f"  - SKIP appt_id={appt.id} reason=already_sent_at={appt.reminder_sent_at}")
                continue

            # normal rejimda 3 urinishdan keyin to'xtatamiz
            if force_id is None and appt.reminder_attempts >= 3:
                continue

            try:
                local_dt = timezone.localtime(appt.scheduled_at)
                local_time_str = local_dt.strftime("%Y-%m-%d %H:%M")

                minutes_left = max(0, math.ceil((appt.scheduled_at - now).total_seconds() / 60))

                text = (
                    f"Siz {local_time_str} ga barberga yozilgansiz. "
                    f"Navbatingizga {minutes_left} daqiqa qoldi. Iltimos, vaqtida keling."
                )

                if dry_run:
                    self.stdout.write(f"  - DRY appt_id={appt.id} phone={appt.phone} msg={text}")
                    continue

                eskiz_id = client.send_sms(appt.phone, text)

                appt.eskiz_request_id = eskiz_id or None
                appt.reminder_sent_at = timezone.now()
                appt.last_reminder_error = None
                appt.save(update_fields=["eskiz_request_id", "reminder_sent_at", "last_reminder_error"])

                self.stdout.write(f"  + SENT appt_id={appt.id} eskiz_id={eskiz_id}")

            except Exception as e:
                appt.reminder_attempts += 1
                appt.last_reminder_error = str(e)
                appt.save(update_fields=["reminder_attempts", "last_reminder_error"])
                self.stdout.write(f"  ! ERROR appt_id={appt.id} err={e}")
