from django.contrib import admin

from korty.models import Lokalizacja, Kort, GodzinyOtwarcia, Rezerwacja, Wydarzenia, Profil

# Register your models here.
admin.site.register(Lokalizacja)
admin.site.register(Kort)
admin.site.register(GodzinyOtwarcia)
admin.site.register(Profil)
admin.site.register(Rezerwacja)
admin.site.register(Wydarzenia)


class RezerwacjaAdmin(admin.ModelAdmin):
    list_display = ('kort', 'profil', 'data', 'godzina')
    readonly_fields = ('status',)



