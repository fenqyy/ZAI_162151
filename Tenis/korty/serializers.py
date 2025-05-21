from rest_framework import serializers
from django.contrib.auth.models import User
from korty.models import *
from rest_framework_simplejwt.tokens import RefreshToken


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil
        fields = ['user', 'telefon', 'avatar']
    user = serializers.CharField(source='user.username', read_only=True)



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
        read_only_fields = ['profil', 'kort', 'status']

    def validate(self, data):
        kort = self.context['kort']
        data_rezerwacji = data['data']
        godzina_start = data['godzina_start']
        godzina_koniec = data['godzina_koniec']

        kolizje = Rezerwacja.objects.filter(
            kort=kort,
            data=data_rezerwacji
        ).exclude(
            godzina_start__gte=godzina_koniec
        ).exclude(
            godzina_koniec__lte=godzina_start
        )

        if kolizje.exists():
            raise serializers.ValidationError(
                f"Kort jest już zarezerwowany w tym czasie."
            )

        dni_map = {
            'monday': 'Poniedziałek',
            'tuesday': 'Wtorek',
            'wednesday': 'Środa',
            'thursday': 'Czwartek',
            'friday': 'Piątek',
            'saturday': 'Sobota',
            'sunday': 'Niedziela',
        }
        dzien_ang = data_rezerwacji.strftime('%A').lower()
        dzien_pl = dni_map.get(dzien_ang)

        godziny = GodzinyOtwarcia.objects.filter(kort=kort, dzien_tygodnia=dzien_pl)

        if not godziny.exists():
            raise serializers.ValidationError(
                f"Kort nieczynny w dniu: {dzien_pl}"
            )

        start_dt = datetime.combine(data_rezerwacji, godzina_start)
        koniec_dt = datetime.combine(data_rezerwacji, godzina_koniec)

        for g in godziny:
            otwarcie = datetime.combine(data_rezerwacji, g.godzina_otwarcia)
            zamkniecie = datetime.combine(data_rezerwacji, g.godzina_zamkniecia)
            if otwarcie <= start_dt and koniec_dt <= zamkniecie:
                break
        else:
            raise serializers.ValidationError(
                f"Rezerwacja poza godzinami otwarcia kortu."
            )

        return data


class WydarzeniaSerializer(serializers.ModelSerializer):
    ile_uczestnikow = serializers.IntegerField(read_only=True)
    uczestnicy = ProfilSerializer(many=True, read_only=True)

    class Meta:
        model = Wydarzenia
        fields = '__all__'
