from datetime import datetime, date
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Event, Certificate, AuditLog
from .forms import RegisterForm, EditProfileForm, LoginForm, EventForm
from .utils import registrar_log, send_welcome_email

# PDF libs
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet

# REST Framework
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .serializers import EventSerializer, EventCreateSerializer 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.exceptions import PermissionDenied
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import os
from django.conf import settings
from .models import Registration
import os
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet

from .models import Event, Certificate, User
User = get_user_model()

# ---------------- HOME ----------------
def home_view(request):
    events = Event.objects.all()
    return render(request, 'core/home.html', {'events': events})

# ---------------- EVENT LIST (WEB) --------------
def event_list(request):
    events = Event.objects.all()
    return render(request, 'core/event_list.html', {'events': events})

# ---------------- EVENT DETAIL -----------------
@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registered = request.user in event.participants.all()
    is_organizer = request.user.role == 'organizer'
    participants = event.participants.all()

    if request.method == "POST":
        # Inscrição
        if 'subscribe' in request.POST and not registered:
            if event.participants.count() >= event.max_participants:
                messages.error(request, "Limite de vagas atingido.")
            else:
                event.participants.add(request.user)
                messages.success(request, 'Inscrição realizada!')
                registrar_log(
                    user=request.user,
                    action="CREATE",
                    model="Registration",
                    object_id=f"{request.user.id}-{event.id}",
                    description=f"Usuário {request.user.username} inscrito no evento {event.title}"
                )
                return redirect('core:event_detail', event_id=event.id)
        # Cancelamento
        elif 'unsubscribe' in request.POST and registered:
            event.participants.remove(request.user)
            messages.success(request, 'Inscrição cancelada!')
            registrar_log(
                user=request.user,
                action="DELETE",
                model="Registration",
                object_id=f"{request.user.id}-{event.id}",
                description=f"Usuário {request.user.username} cancelou a inscrição no evento {event.title}"
            )
            return redirect('core:event_detail', event_id=event.id)

    return render(request, 'core/event_detail.html', {
        'event': event,
        'registered': registered,
        'is_organizer': is_organizer,
        'participants': participants,
        'participants_count': participants.count(),  # 👈 novo
    })

# ---------------- PROFILE -----------------
@login_required
def profile_view(request):
    user = request.user
    return render(request, 'core/profile.html', {
        'user': user,
        'registered_events': Event.objects.filter(participants=user),
        'organized_events': Event.objects.filter(organizer=user) if user.role == 'organizer' else None,
    })

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado!")
            return redirect('core:profile')
        messages.error(request, "Corrija os erros abaixo.")
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'core/edit_profile.html', {'form': form})

# ---------------- AUTH -----------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f"http://127.0.0.1:8000/activate/{uid}/"
            send_welcome_email(user, link)
            # não usar messages.success aqui
            return redirect('core:home')
    else:
        form = RegisterForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('core:home')
            messages.error(request, "Credenciais inválidas.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def activate_user(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user.is_active = True
        user.save()
        messages.success(request, "Conta ativada! Agora você pode fazer login.")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Link inválido ou expirado.")
    return redirect('core:login')

@login_required
def logout_view(request):
    logout(request)
    list(messages.get_messages(request))  # limpa mensagens pendentes
    return redirect('core:login')

# ---------------- EVENT CREATE / EDIT / DELETE -----------------
@login_required
def create_event_view(request):
    if request.user.role != 'organizer':
        messages.error(request, "Apenas organizadores podem criar eventos.")
        return redirect('core:home')
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, "Evento criado!")
            registrar_log(
                user=request.user,
                action="CREATE",
                model="Event",
                object_id=event.id,
                description=f"Evento {event.title} criado"
            )
            return redirect('core:event_detail', event_id=event.id)
        messages.error(request, "Corrija os erros.")
    else:
        form = EventForm()
    return render(request, 'core/event_form.html', {'form': form})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.organizer:
        messages.error(request, "Você não pode editar esse evento.")
        return redirect('core:event_detail', event_id=event_id)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento atualizado!")
            return redirect('core:event_detail', event_id=event.id)
        else:
            messages.error(request, "Corrija os erros abaixo.")  # 👈 garante feedback
    else:
        form = EventForm(instance=event)

    return render(request, 'core/edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.organizer:
        messages.error(request, "Sem permissão.")
        return redirect('core:event_detail', event_id=event.id)
    if request.method == "POST":
        registrar_log(
            user=request.user,
            action="DELETE",
            model="Event",
            object_id=event.id,
            description=f"Evento {event.title} excluído"
        )
        event.delete()
        messages.success(request, "<b>Evento excluído com sucesso!</b>")
        return redirect('core:events')
    return render(request, 'core/event_confirm_delete.html', {'event': event})

# ---------------- CERTIFICATE ---------------

@login_required
def emitir_certificado(request, event_id, user_id):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(User, id=user_id)

    # Apenas organizador pode emitir
    if request.user.role != 'organizer':
        return HttpResponse("Sem permissão.", status=403)

    # Só pode emitir para inscritos
    if not event.participants.filter(id=user.id).exists():
        return HttpResponse("Usuário não inscrito.", status=403)

    # Registrar emissão no banco
    certificado, created = Certificate.objects.get_or_create(user=user, event=event)

    # Configuração do PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{user.username}_{event.title}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Fundo branco
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1)

    # Moldura roxa
    c.setStrokeColor(colors.HexColor("#43054E"))
    c.setLineWidth(4)
    c.rect(2*cm, 2*cm, width - 4*cm, height - 4*cm, stroke=1, fill=0)

    # Logo centralizada
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'image', 'sgea.jpg')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, x=width/2 - 2*cm, y=height - 6*cm,
                    width=4*cm, height=4*cm, preserveAspectRatio=True, mask='auto')

    # Título
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor("#43054E"))
    c.drawCentredString(width/2, height - 7.5*cm, "Certificado de Participação")

    # Texto central
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.alignment = 1
    style.fontName = 'Helvetica'
    style.fontSize = 14
    style.leading = 22

    text = f"""
    Certificamos que <b>{user.first_name or user.username}</b> participou do evento
    <b>{event.title}</b>, realizado de {event.start_date.strftime('%d/%m/%Y')} 
    a {event.end_date.strftime('%d/%m/%Y')}, no local {event.location}.
    """
    para = Paragraph(text, style)
    frame = Frame(3*cm, height/2 - 3*cm, width - 6*cm, 6*cm, showBoundary=0)

    frame.addFromList([para], c)

    # Rodapé com data e assinatura
    data_hora = datetime.now().strftime('%d/%m/%Y, às %H:%M')
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, 4*cm, f"Emitido em {data_hora}")

    c.setFont("Helvetica", 12)
    c.drawString(width - 9*cm, 3.1*cm, "________________________")
    c.drawString(width - 8.8*cm, 2.5*cm, "Assinatura do Organizador")

    c.showPage()
    c.save()
    return response


# ---------------- API THROTTLE -----------------
class EventListThrottle(UserRateThrottle):
    scope = 'events_list'

class EventRegisterThrottle(UserRateThrottle):
    scope = 'events_register'

# ---------------- API -----------------
class EventListAPI(generics.ListAPIView):
    queryset = Event.objects.all().order_by("start_date")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [EventListThrottle]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        registrar_log(
            user=request.user,
            action="READ",
            model="Event",
            object_id="ALL",
            description=f"Usuário {request.user.username} consultou lista de eventos via API"
        )
        return response

class EventCreateAPI(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'organizer':
            raise PermissionError("Apenas organizadores podem criar eventos.")
        event = serializer.save(organizer=self.request.user)
        registrar_log(
            user=self.request.user,
            action="CREATE",
            model="Event",
            object_id=event.id,
            description=f"Evento {event.title} criado via API"
        )


class EventRegisterAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [EventRegisterThrottle]

    def post(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Evento não encontrado."}, status=404)

        if event.participants.filter(id=user.id).exists():
            return Response({"error": "Usuário já inscrito."}, status=400)
        if event.participants.count() >= event.max_participants:
            return Response({"error": "Limite de vagas atingido."}, status=400)

        event.participants.add(user)
        registrar_log(
            user=user,
            action="CREATE",
            model="Registration",
            object_id=f"{user.id}-{event.id}",
            description=f"Usuário {user.username} inscrito no evento {event.title}"
        )
        return Response({"success": "Inscrição realizada!"})



class EventCancelAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Evento não encontrado."}, status=404)

        if request.user not in event.participants.all():
            return Response({"error": "Você não está inscrito."}, status=400)

        event.participants.remove(request.user)
        registrar_log(
            user=request.user,
            action="DELETE",
            model="Registration",
            object_id=f"{request.user.id}-{event.id}",
            description=f"Usuário {request.user.username} cancelou inscrição no evento {event.title}"
        )
        return Response({"success": "Inscrição removida!"})


class MyEventsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(participants=request.user)
        return Response(EventSerializer(events, many=True).data)


# ---------------- EMAIL PREVIEW -----------------
@login_required
def preview_email(request):
    user = request.user
    context = {"user": user, "link": "http://127.0.0.1:8000/login/"}
    return render(request, "core/welcome_email.html", context)

# ---------------- AUDITORIA -----------------
@login_required
def audit_logs(request):
    if request.user.role != "organizer":
        messages.error(request, "Apenas organizadores podem visualizar os logs.")
        return redirect("core:home")
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, "core/audit_logs.html", {"logs": logs})
