from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cancel/<int:pk>/", views.cancel_appointment, name="cancel_appointment"),
]
