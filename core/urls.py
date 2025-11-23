from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .views import (
    preview_email,
    MyEventsAPI,
    EventCancelAPI,
    audit_logs
)

app_name = 'core'

urlpatterns = [
    # Páginas principais
    path('', views.home_view, name='home'),
    path('events/', views.event_list, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/new/', views.create_event_view, name='event_form'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='event_delete'),

    # Perfil
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Autenticação
    path('register/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Certificados
    path('certificado/<int:event_id>/<int:user_id>/', views.emitir_certificado, name='emitir_certificado'),

    # API JWT
    path('api/token/a', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Eventos
    path('api/events/', views.EventListAPI.as_view(), name='api_events_list'),
    path('api/events/create/', views.EventCreateAPI.as_view(), name='api_event_create'),
    path('api/events/<int:event_id>/register/', views.EventRegisterAPI.as_view(), name='api_event_register'),
    path('api/events/<int:event_id>/cancel/', EventCancelAPI.as_view(), name='api_event_cancel'),
    path('api/my-events/', MyEventsAPI.as_view(), name='api_my_events'),

    # Pré-visualização de email
    path("preview-email/", preview_email, name="preview_email"),

    # AUDITORIA / LOGS
    path("logs/", audit_logs, name="audit_logs"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
