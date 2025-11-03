from django.urls import path
from django.conf import settings
from django.conf.urls.static import static  
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import MyEventsAPI, EventCancelAPI


app_name = 'core'

urlpatterns = [
    # -----------------------------
    # Rotas do sistema principal
    # -----------------------------
    path('', views.home_view, name='home'),
    path('events/', views.event_list, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/new/', views.create_event_view, name='event_form'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('register/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('certificado/<int:event_id>/<int:user_id>/', views.emitir_certificado, name='emitir_certificado'),

    # -----------------------------
    # API JWT
    # -----------------------------
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # -----------------------------
    # API Eventos
    # -----------------------------
    path('api/events/', views.EventListAPI.as_view(), name='api_events_list'),
    path('api/events/create/', views.EventCreateAPI.as_view(), name='api_event_create'),
    path('api/events/<int:event_id>/register/', views.EventRegisterAPI.as_view(), name='api_event_register'),

# Meus eventos (inscrições do usuário)
    path('api/my-events/', MyEventsAPI.as_view(), name='api_my_events'),

# Cancelar inscrição
    path('api/events/<int:event_id>/cancel/', EventCancelAPI.as_view(), name='api_event_cancel'),
]
# Servir arquivos de mídia em DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
