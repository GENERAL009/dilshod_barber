from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views
from .api_views import AppointmentViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cancel/<int:pk>/", views.cancel_appointment, name="cancel_appointment"),
    path("trigger-reminders/", views.trigger_reminders, name="trigger_reminders"),
    path("api/", include(router.urls)),
    
    # Swagger UI:
    path('api/swagger/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/swagger/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
