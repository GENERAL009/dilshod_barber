import re
from django import forms
from django.utils import timezone
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Appointment
        fields = ["phone", "scheduled_at"]

    def clean_phone(self):
        raw = self.cleaned_data["phone"]

        # faqat raqam qoldiramiz (bo'sh joy, +, va h.k. olib tashlanadi)
        digits = re.sub(r"\D", "", str(raw))

        # Agar user 9 ta raqam kiritsa -> 998 qo'shamiz
        if len(digits) == 9:
            return "998" + digits

        # Agar user to'liq 998XXXXXXXXX kiritib yuborsa ham qabul qilamiz
        if len(digits) == 12 and digits.startswith("998"):
            return digits

        raise forms.ValidationError("Telefon 9 ta raqam bo'lsin (masalan 901234567) yoki 998901234567.")

    def clean_scheduled_at(self):
        dt = self.cleaned_data["scheduled_at"]
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
