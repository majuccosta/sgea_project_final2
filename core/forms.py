from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Event
from django.core.exceptions import ValidationError
import datetime

User = get_user_model()

# ------------------ REGISTER FORM ------------------

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Nome', max_length=50)
    last_name = forms.CharField(label='Sobrenome', max_length=50)

    phone = forms.CharField(
        label="Telefone",
        widget=forms.TextInput(attrs={'placeholder': '(00) 00000-0000'})
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'password1',
            'password2',
            'role'
        ]


# ------------------ EDIT PROFILE FORM ------------------

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=50)
    last_name = forms.CharField(label='Sobrenome', max_length=50)
    email = forms.EmailField(label='Email')

    phone = forms.CharField(
        label="Telefone",
        widget=forms.TextInput(attrs={'placeholder': '(00) 00000-0000'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']


# ------------------ LOGIN FORM ------------------

class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário', max_length=50)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)


# ------------------ EVENT FORM ------------------
# ------------------ EVENT FORM ------------------
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'event_type', 'start_date', 'end_date',
            'start_time', 'end_time', 'location', 'description',
            'max_participants', 'banner'
        ]

        # 🏷️ Rótulos em português
        labels = {
            'title': 'Título do Evento',
            'event_type': 'Tipo de Evento',
            'start_date': 'Data de Início',
            'end_date': 'Data de Término',
            'start_time': 'Hora de Início',
            'end_time': 'Hora de Término',
            'location': 'Local',
            'description': 'Descrição',
            'max_participants': 'Número Máximo de Participantes',
            'banner': 'Banner do Evento',
        }

        # ✏️ Campos personalizados com placeholders e tipos corretos
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Digite o título do evento'
            }),
            'event_type': forms.Select(),
            'start_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Digite o local do evento'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Descreva brevemente o evento...',
                'rows': 3
            }),
            'max_participants': forms.NumberInput(attrs={
                'placeholder': 'Ex: 50'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # 🚫 Data de início não pode ser anterior a hoje
        if start_date and start_date < datetime.date.today():
            raise ValidationError("⚠️ A data de início não pode ser anterior a hoje.")

        # 🚫 Data de término não pode ser anterior à data de início
        if start_date and end_date and end_date < start_date:
            raise ValidationError("⚠️ A data de término não pode ser anterior à data de início.")

        # 🚫 Hora de término deve ser posterior à hora de início (no mesmo dia)
        if start_date == end_date and start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("⚠️ A hora de término deve ser posterior à hora de início.")

        return cleaned_data

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')
        if banner:
            if not banner.content_type.startswith('image'):
                raise ValidationError("O arquivo deve ser uma imagem (jpg, png, etc).")
            if banner.size > 5 * 1024 * 1024:
                raise ValidationError("O tamanho da imagem não pode ultrapassar 5MB.")
        return banner
