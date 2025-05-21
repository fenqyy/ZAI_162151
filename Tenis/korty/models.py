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
            self.status = "zajete"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rezerwacja {self.kort} na {self.data} od {self.godzina_start} do {self.godzina_koniec}, status: {self.status}"

    class Meta:
        verbose_name_plural = "Rezerwacje"


class Wydarzenia(models.Model):
    nazwa = models.CharField(max_length=200)
    data = models.DateTimeField()
    uczestnicy = models.ManyToManyField('Profil')

    def __str__(self):
        return f'Wydarzenie {self.nazwa} odbędzie sie {self.data}'

    class Meta:
        verbose_name_plural = "Wydarzenia"