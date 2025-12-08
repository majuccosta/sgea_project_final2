from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import re
from .models import Event

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

    # Validação de senha
    def clean_password2(self):
        password = self.cleaned_data.get("password2")
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).{8,}$', password):
            raise ValidationError(
                "A senha deve ter no mínimo 8 caracteres, incluindo letras, números e caracteres especiais."
            )
        return password

    # Validação de telefone
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)  # Remove caracteres não numéricos
        if len(digits) != 11:
            raise ValidationError("O telefone deve conter 11 dígitos (ex: 11999999999).")
        return phone


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

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if len(digits) != 11:
            raise ValidationError("O telefone deve conter 11 dígitos (ex: 11999999999).")
        return phone


# ------------------ LOGIN FORM ------------------
class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário', max_length=50)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)


# ------------------ EVENT FORM ------------------

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'event_type', 'start_date', 'end_date',
            'start_time', 'end_time', 'location', 'description',
            'max_participants', 'banner'
        ]
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
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Digite o título do evento'}),
            'event_type': forms.Select(),
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'location': forms.TextInput(attrs={'placeholder': 'Digite o local do evento'}),
            'description': forms.Textarea(attrs={'placeholder': 'Descreva brevemente o evento...', 'rows': 3}),
            'max_participants': forms.NumberInput(attrs={'placeholder': 'Ex: 50'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preenche datas e horários ao editar
        for field in ['start_date', 'end_date']:
            if self.instance and getattr(self.instance, field):
                self.fields[field].initial = getattr(self.instance, field).strftime('%Y-%m-%d')
        for field in ['start_time', 'end_time']:
            if self.instance and getattr(self.instance, field):
                self.fields[field].initial = getattr(self.instance, field).strftime('%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Validação de datas
        if start_date and start_date < date.today():
            raise ValidationError("⚠️ A data de início não pode ser anterior a hoje.")
        if start_date and end_date and end_date < start_date:
            raise ValidationError("⚠️ A data de término não pode ser anterior à data de início.")
        if start_date == end_date and start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("⚠️ A hora de término deve ser posterior à hora de início.")
        if start_date and start_date > date.today() + timedelta(days=365*5):
            raise ValidationError("⚠️ A data de início é muito distante no futuro.")

        return cleaned_data



    def clean_max_participants(self):
        max_p = self.cleaned_data.get('max_participants')
        if max_p is not None and max_p <= 0:
            raise ValidationError("O número de participantes deve ser maior que zero.")
        return max_p

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')
        if not banner:
            return banner

        if hasattr(banner, 'content_type'):
            if not banner.content_type.startswith('image'):
                raise ValidationError("O arquivo deve ser uma imagem (jpg, png, etc).")

        # Verifica extensão
        valid_extensions = ['jpg', 'jpeg', 'png']
        if not any([banner.name.lower().endswith(ext) for ext in valid_extensions]):
            raise ValidationError("O arquivo deve ter extensão jpg, jpeg ou png.")

        if banner.size > 5 * 1024 * 1024:
            raise ValidationError("O tamanho da imagem não pode ultrapassar 5MB.")

        return banner
