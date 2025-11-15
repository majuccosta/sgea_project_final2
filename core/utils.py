from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    subject = "🎉 Bem-vindo(a) ao SGEA!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    # Dados que serão enviados ao template do e-mail
    context = {
        'user': user,
        'login_url': 'http://127.0.0.1:8000/login/',  # ajuste conforme o domínio real
    }

    # Gera o HTML do e-mail
    html_content = render_to_string('emails/welcome_email.html', context)

    # Cria a mensagem
    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
