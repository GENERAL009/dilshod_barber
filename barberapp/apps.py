import os
import sys
from django.apps import AppConfig
from django.conf import settings


class BarberappConfig(AppConfig):
    name = "barberapp"

    def ready(self):
        # ✅ faqat runserver ishlaganda ishga tushsin (shell/migrate paytida emas)
        if "runserver" not in sys.argv:
            return

        # ✅ autoreload 2 marta ishga tushirmasin
        run_main = os.environ.get("RUN_MAIN", "")
        is_reloader = run_main.lower() == "true"
        if settings.DEBUG and not (is_reloader or "--noreload" in sys.argv):
            return

        from .reminder_worker import start_worker
        start_worker()
        print("[reminder_worker] started")
