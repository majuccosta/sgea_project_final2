from datetime import datetime, date
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Event, Certificate
from .forms import RegisterForm, EditProfileForm, LoginForm, EventForm

# PDF libs
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet

# REST Framework
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer, EventCreateSerializer

# Email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
        if 'subscribe' in request.POST and not registered:
            event.participants.add(request.user)
            messages.success(request, 'Inscrição realizada com sucesso!')
            return redirect('core:event_detail', event_id=event.id)

        elif 'unsubscribe' in request.POST and registered:
            event.participants.remove(request.user)
            messages.success(request, 'Inscrição cancelada!')
            return redirect('core:event_detail', event_id=event.id)

    return render(request, 'core/event_detail.html', {
        'event': event,
        'registered': registered,
        'is_organizer': is_organizer,
        'participants': participants,
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


# ---------------- AUTH ----------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            subject = "Bem-vindo ao SGEA 🎓"
            context = {
                'user': user,
                'link': 'http://127.0.0.1:8000/login/',
            }

            html_content = render_to_string("core/welcome_email.html", context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            messages.success(request, "Cadastro realizado com sucesso! Verifique seu e-mail.")
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


@login_required
def logout_view(request):
    logout(request)
    return redirect('core:login')


# ---------------- EVENT CREATE -----------------
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
            return redirect('core:event_detail', event_id=event.id)
        messages.error(request, "Corrija os erros.")
    else:
        form = EventForm()

    return render(request, 'core/event_form.html', {'form': form})


# ---------------- EVENT EDIT -----------------
@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.organizer:
        messages.error(request, "Você não pode editar esse evento.")
        return redirect('core:event_detail', event_id=event_id)

    if event.start_date < date.today():
        messages.error(request, "Evento já passou.")
        return redirect('core:event_detail', event_id=event_id)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento atualizado!")
            return redirect('core:event_detail', event_id=event.id)
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
        event.delete()
        messages.success(request, "Evento excluído!")
        return redirect('core:events')

    return render(request, 'core/event_confirm_delete.html', {'event': event})


# ---------------- CERTIFICATE -----------------
def emitir_certificado(request, event_id, user_id):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(User, id=user_id)

    if request.user.role != 'organizer':
        return HttpResponse("Sem permissão.", status=403)

    if not event.participants.filter(id=user.id).exists():
        return HttpResponse("Usuário não inscrito.", status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"certificado_{user.username}_{event.title}.pdf\"'  

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1)

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width/2, height - 100, "Certificado de Participação")

    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.alignment = 1
    style.fontSize = 14
    style.leading = 22

    text = f"""
    Certificamos que {user.first_name or user.username} participou do evento
    '{event.title}' realizado de {event.start_date.strftime('%d/%m/%Y')} 
    a {event.end_date.strftime('%d/%m/%Y')}.
    """

    para = Paragraph(text, style)
    frame = Frame(50, height/2 - 60, width - 100, 200, showBoundary=0)
    frame.addFromList([para], c)

    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, 100, f"Emitido em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.showPage()
    c.save()
    return response


# ---------------- API -----------------
class EventListAPI(generics.ListAPIView):
    queryset = Event.objects.all().order_by("start_date")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventCreateAPI(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'organizer':
            raise PermissionError("Apenas organizadores podem criar eventos.")
        serializer.save(organizer=self.request.user)


class EventRegisterAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Evento não encontrado."}, status=404)

        if event.participants.filter(id=user.id).exists():
            return Response({"error": "Usuário já inscrito."}, status=400)

        event.participants.add(user)
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
        return Response({"success": "Inscrição removida!"})


class MyEventsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(participants=request.user)
        return Response(EventSerializer(events, many=True).data)


# PREVIEW DO E-MAIL
def preview_email(request):
    user = request.user
    context = {
        "user": user,
        "link": "http://127.0.0.1:8000/login/"
    }
    return render(request, "core/welcome_email.html", context)
