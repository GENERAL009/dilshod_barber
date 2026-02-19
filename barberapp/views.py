from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import AppointmentForm
from .models import Appointment


def dashboard(request):
    # 1) POST -> yangi appointment yaratish
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            # Saqlagandan keyin shu tanlangan kunga qaytarish (agar filter bo'lsa)
            date_q = request.GET.get("date")
            return redirect(f"/?date={date_q}" if date_q else "/")
    else:
        form = AppointmentForm()

    # 2) GET -> date filter (default: bugun)
    date_str = request.GET.get("date")  # YYYY-MM-DD
    selected_date = parse_date(date_str) if date_str else timezone.localdate()

    if not selected_date:
        selected_date = timezone.localdate()  # noto'g'ri format bo'lsa ham bugun

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
            "form": form,
            "appts": appts,
            "selected_date": selected_date,
        },
    )


def cancel_appointment(request, pk: int):
    Appointment.objects.filter(pk=pk).update(status="cancelled")
    return redirect("dashboard")
