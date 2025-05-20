from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Lokalizacja(models.Model):
    miasto = models.CharField(max_length=100, blank=False)
    adres = models.CharField(max_length=255)
    kod_pocztowy = models.CharField(max_length=6)

    def __str__(self):
        return f'{self.miasto}, {self.adres}, {self.kod_pocztowy}'

    class Meta:
        verbose_name_plural = "Lokalizacja"


class Kort(models.Model):
    TYPY = [
        ("trawiasty", "Trawiasty"),
        ("mączka", "Mączka"),
        ("twardy", "Twardy"),
        ("dywanowy", "Dywanowy")
    ]
    nazwa = models.CharField(max_length=100)
    lokalizacja = models.ForeignKey(Lokalizacja, on_delete=models.CASCADE)
    typ = models.CharField(max_length=50, choices=TYPY)

    def __str__(self):
        return f"{self.nazwa} ({self. lokalizacja}), typ: {self.typ}"

    class Meta:
        verbose_name_plural = "Kort"


class GodzinyOtwarcia(models.Model):
    kort = models.ForeignKey(Kort, on_delete=models.CASCADE)
    dzien_tygodnia = models.CharField(max_length=20)
    godzina_otwarcia = models.TimeField()
    godzina_zamkniecia = models.TimeField()

    def __str__(self):
        return f"{self.kort} - {self.dzien_tygodnia} od: {self.godzina_otwarcia}, do: {self.godzina_zamkniecia}"

    class Meta:
        verbose_name_plural = "Godziny Otwarcia"


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=9, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatary/", blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Profil"


class Rezerwacja(models.Model):
    kort = models.ForeignKey(Kort, on_delete=models.CASCADE)
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    data = models.DateField()
    godzina_start = models.TimeField(blank=True, null=True)
    godzina_koniec = models.TimeField(blank=True, null=True)
    STATUSY = [
        ("wolne", "Wolne"),
        ("zajete", "Zajęte"),
    ]
    status = models.CharField(max_length=20, choices=STATUSY, default="wolne", editable=False)

    def save(self, *args, **kwargs):
        if self.godzina_start and self.godzina_koniec:
            rezerwacje = Rezerwacja.objects.filter(kort=self.kort, data=self.data)
            for rezerwacja in rezerwacje:
                if not (
                        self.godzina_koniec <= rezerwacja.godzina_start or self.godzina_start >= rezerwacja.godzina_koniec):
                    raise ValidationError(
                        f"Kort jest już zarezerwowany w tym czasie (od {rezerwacja.godzina_start} do {rezerwacja.godzina_koniec}).")

        dni_tygodnia_map = {
            'monday': 'Poniedziałek',
            'tuesday': 'Wtorek',
            'wednesday': 'Środa',
            'thursday': 'Czwartek',
            'friday': 'Piątek',
            'saturday': 'Sobota',
            'sunday': 'Niedziela',
        }

        dzien_tygodnia_ang = self.data.strftime('%A').lower()
        dzien_tygodnia_pl = dni_tygodnia_map.get(dzien_tygodnia_ang)

        if not dzien_tygodnia_pl:
            raise ValidationError("Nie udało się odczytać dnia tygodnia.")

        godziny_otwarcia = GodzinyOtwarcia.objects.filter(kort=self.kort, dzien_tygodnia=dzien_tygodnia_pl)

        if not godziny_otwarcia.exists():
            raise ValidationError(f"Kort nie jest otwarty w dniu {self.data.strftime('%A')}.")

        godzina_start_obj = datetime.combine(self.data, self.godzina_start)
        godzina_koniec_obj = datetime.combine(self.data, self.godzina_koniec)

        for godzina in godziny_otwarcia:
            godzina_otwarcia = datetime.combine(self.data, godzina.godzina_otwarcia)
            godzina_zamkniecia = datetime.combine(self.data, godzina.godzina_zamkniecia)

            if not (godzina_koniec_obj <= godzina_otwarcia or godzina_start_obj >= godzina_zamkniecia):
                break
        else:
            raise ValidationError(
                f"Rezerwacja nie mieści się w godzinach otwarcia kortu w dniu {self.data.strftime('%A')}.")

        self.status = "zajete"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rezerwacja {self.kort} na {self.data} od {self.godzina_start} do {self.godzina_koniec}, status: {self.status}"

    class Meta:
        verbose_name_plural = "Rezerwacja"


class Wydarzenia(models.Model):
    nazwa = models.CharField(max_length=200)
    data = models.DateTimeField()
    uczestnicy = models.ManyToManyField('Profil')

    def __str__(self):
        return f'Wydarzenie {self.nazwa} odbędzie sie {self.data}'

    class Meta:
        verbose_name_plural = "Wydarzenia"