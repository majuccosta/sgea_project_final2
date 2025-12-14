from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Aluno'),
        ('teacher', 'Professor'),
        ('organizer', 'Organizador'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ('workshop', 'Workshop'),
        ('lecture', 'Palestra'),
        ('seminar', 'Seminário'),
        ('educational_week', 'Semana Educativa'),
        ('minicourse', 'Minicurso'),
    )

    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    max_participants = models.PositiveIntegerField()
    description = models.TextField()
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    participants = models.ManyToManyField(
        User,
        related_name='events_participated',
        blank=True
    )
    banner = models.ImageField(
        upload_to='event_banners/',
        null=True,
        blank=True
    )

    def clean(self):
        """
        REGRA DE NEGÓCIO:
        - Hora de término NÃO pode ser igual ou anterior à hora de início.
        (independente da data)
        """
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': "A hora de término deve ser posterior à hora de início."
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # garante validação sempre
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model} - {self.action} - {self.timestamp}"
