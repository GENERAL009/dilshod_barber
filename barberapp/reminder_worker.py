import threading
import time
from django.core.management import call_command
from django.db import close_old_connections

# ✅ shu yerda boshqarasiz (env yo'q)
REMIND_MINUTES = 2        # productionda 30 qiling
POLL_SECONDS = 20         # 20 sekundda bir tekshiradi

_started = False
_lock = threading.Lock()


def start_worker():
    global _started
    with _lock:
        if _started:
            return
        _started = True

    t = threading.Thread(target=_loop, name="reminder-worker", daemon=True)
    t.start()


def _loop():
    while True:
        try:
            close_old_connections()
            # send_reminders management command'ini chaqiramiz
            call_command("send_reminders", minutes=REMIND_MINUTES)
        except Exception as e:
            print(f"[reminder_worker] ERROR: {e}")
        time.sleep(POLL_SECONDS)
