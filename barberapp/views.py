from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import AppointmentForm
from .models import Appointment


def dashboard(request):
    # 1) GET -> faqat bugungi/kelajakdagi navbatlar (view only)
    selected_date = timezone.localdate()
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(
        timezone.datetime.combine(selected_date, timezone.datetime.min.time()),
        tz
    )
    end = start + timezone.timedelta(days=1)

    appts = (
        Appointment.objects
        .filter(scheduled_at__gte=start, scheduled_at__lt=end)
        .order_by("scheduled_at")
    )

    return render(
        request,
        "dashboard.html",
        {
            "appts": appts,
            "selected_date": selected_date,
        },
    )

def management(request):
    # 1) POST -> yangi appointment yaratish
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("management")
    else:
        form = AppointmentForm()

    # 2) GET -> date filter (default: bugun)
    date_str = request.GET.get("date")
    selected_date = parse_date(date_str) if date_str else timezone.localdate()

    if not selected_date:
        selected_date = timezone.localdate()

    tz = timezone.get_current_timezone()
    start = timezone.make_aware(
        timezone.datetime.combine(selected_date, timezone.datetime.min.time()),
        tz
    )
    end = start + timezone.timedelta(days=1)

    appts = (
        Appointment.objects
        .filter(scheduled_at__gte=start, scheduled_at__lt=end)
        .order_by("scheduled_at")
    )

    return render(
        request,
        "management.html",
        {
            "form": form,
            "appts": appts,
            "selected_date": selected_date,
        },
    )


def cancel_appointment(request, pk: int):
    Appointment.objects.filter(pk=pk).update(status="cancelled")
    return redirect("dashboard")

from io import StringIO
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.core.management import call_command

# ✅ uzun, taxmin qilib bo'lmaydigan token qo'ying
REMINDER_TOKEN = "barber_sms_trigger_secret_998"

@csrf_exempt
@require_GET
def trigger_reminders(request):
    if request.GET.get("token", "") != REMINDER_TOKEN:
        return HttpResponseForbidden("bad token")

    minutes = int(request.GET.get("minutes", "30"))  # test uchun 2, prod uchun 30

    out = StringIO()
    call_command("send_reminders", minutes=minutes, stdout=out)

    return JsonResponse({
        "ok": True,
        "minutes": minutes,
        "output": out.getvalue(),
    })
