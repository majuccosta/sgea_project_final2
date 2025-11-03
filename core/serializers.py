from rest_framework import serializers
from .models import Event
from django.contrib.auth import get_user_model

User = get_user_model()

# -----------------------------
# Serializer do usuário
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone']

# -----------------------------
# Serializer para listar eventos
# -----------------------------
class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type',
            'start_date', 'end_date', 'start_time', 'end_time',
            'location', 'max_participants', 'banner',
            'organizer', 'participants'
        ]

# -----------------------------
# Serializer para criar eventos via API
# -----------------------------
class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type',
            'start_date', 'end_date', 'start_time', 'end_time',
            'location', 'max_participants', 'banner'
        ]

    def validate(self, attrs):
        # Validação: data de término não pode ser anterior à data de início
        if attrs.get('end_date') and attrs.get('start_date') and attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError("A data de término não pode ser anterior à data de início.")
        return attrs
