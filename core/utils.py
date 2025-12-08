from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import AuditLog

def send_welcome_email(user, link):
    subject = "🎉 Bem-vindo(a) ao SGEA!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    context = {
        'user': user,
        'link': link,
        'logo_url': settings.BASE_URL + settings.STATIC_URL + 'img/logo_sgea.png'
    }

    html_content = render_to_string('core/welcome_email.html', context)
    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def registrar_log(user=None, action="", model="", object_id="", description=""):
    AuditLog.objects.create(
        user=user,
        action=action,
        model=model,
        object_id=str(object_id),
        description=description
    )
