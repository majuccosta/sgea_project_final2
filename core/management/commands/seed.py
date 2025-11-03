from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Cria usuários iniciais (organizador, professor e aluno)"

    def handle(self, *args, **kwargs):
        users = [
            {"username": "organizador", "password": "Admin@123", "role": "organizer", "email": "organizador@sgea.com"},
            {"username": "professor", "password": "Professor@123", "role": "teacher", "email": "professor@sgea.com"},
            {"username": "aluno", "password": "Aluno@123", "role": "student", "email": "aluno@sgea.com"},
        ]

        for user in users:
            if not User.objects.filter(username=user["username"]).exists():
                User.objects.create_user(
                    username=user["username"],
                    password=user["password"],
                    role=user["role"],
                    email=user["email"]
                )

        self.stdout.write(self.style.SUCCESS("Usuários padrão criados com sucesso!"))
