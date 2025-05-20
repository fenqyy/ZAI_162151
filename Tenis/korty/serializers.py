from rest_framework import serializers
from django.contrib.auth.models import User
from korty.models import *
from rest_framework_simplejwt.tokens import RefreshToken


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil
        fields = ['telefon', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    profil = ProfilSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profil']

    def create(self, validated_data):
        profil_data = validated_data.pop('profil', None)
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email')
        )
        user.set_password(validated_data['password'])
        user.save()

        if profil_data:
            Profil.objects.create(user=user, **profil_data)

        return user

    def update(self, instance, validated_data):
        profil_data = validated_data.pop('profil', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if profil_data:
            profil, created = Profil.objects.get_or_create(user=instance)
            for attr, value in profil_data.items():
                setattr(profil, attr, value)
            profil.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class LokalizacjaSerializer(serializers.ModelSerializer):
    ile_kortow = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lokalizacja
        fields = '__all__'


class KortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kort
        fields = '__all__'


class GodzinyOtwarciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GodzinyOtwarcia
        fields = '__all__'


class RezerwacjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rezerwacja
        fields = '__all__'
        read_only_fields = ['profil', 'kort']

    def validate(self, data):
        kort = self.context['kort']
        data_rezerwacji = data['data']
        godzina_start = data['godzina_start']
        godzina_koniec = data['godzina_koniec']

        istniejące_rezerwacje = Rezerwacja.objects.filter(kort=kort, data=data_rezerwacji)

        for istniejąca in istniejące_rezerwacje:
            if not (godzina_koniec <= istniejąca.godzina_start or godzina_start >= istniejąca.godzina_koniec):
                raise serializers.ValidationError(
                    f"Kort jest już zarezerwowany w tym czasie: od {istniejąca.godzina_start} do {istniejąca.godzina_koniec}."
                )

        return data


class WydarzeniaSerializer(serializers.ModelSerializer):
    ile_uczestnikow = serializers.IntegerField(read_only=True)
    class Meta:
        model = Wydarzenia
        fields = '__all__'
