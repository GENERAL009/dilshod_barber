from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['created_at', 'reminder_sent_at', 'reminder_attempts', 'last_reminder_error', 'eskiz_request_id']
