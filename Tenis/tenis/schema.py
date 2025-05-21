import graphene
import graphql_jwt
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from korty.models import Kort, GodzinyOtwarcia, Lokalizacja


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class GodzinyOtwarciaType(DjangoObjectType):
    class Meta:
        model = GodzinyOtwarcia
        fields = '__all__'


class KortType(DjangoObjectType):
    class Meta:
        model = Kort
        fields = '__all__'


class Query(graphene.ObjectType):
    all_korty = graphene.List(KortType)

    def resolve_all_korty(self, info):
        return Kort.objects.all()


class CreateKort(graphene.Mutation):
    kort = graphene.Field(KortType)

    class Arguments:
        nazwa = graphene.String(required=True)
        lokalizacja_id = graphene.ID(required=True)
        typ = graphene.String(required=True)

    def mutate(self, info, nazwa, lokalizacja_id, typ):
        lokalizacja = Lokalizacja.objects.get(pk=lokalizacja_id)
        kort = Kort(nazwa=nazwa, lokalizacja=lokalizacja, typ=typ)
        kort.save()
        return CreateKort(kort=kort)


class UpdateKort(graphene.Mutation):
    kort = graphene.Field(KortType)

    class Arguments:
        id = graphene.ID(required=True)
        nazwa = graphene.String()
        lokalizacja_id = graphene.ID()
        typ = graphene.String()

    def mutate(self, info, id, nazwa=None, lokalizacja_id=None, typ=None):
        kort = Kort.objects.get(pk=id)
        if nazwa:
            kort.nazwa = nazwa
        if lokalizacja_id:
            kort.lokalizacja = Lokalizacja.objects.get(pk=lokalizacja_id)
        if typ:
            kort.typ = typ
        kort.save()
        return UpdateKort(kort=kort)


class DeleteKort(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        kort = Kort.objects.get(pk=id)
        kort.delete()
        return DeleteKort(ok=True)


class CreateGodzinyOtwarcia(graphene.Mutation):
    godziny_otwarcia = graphene.Field(GodzinyOtwarciaType)

    class Arguments:
        kort_id = graphene.ID(required=True)
        dzien_tygodnia = graphene.String(required=True)
        godzina_otwarcia = graphene.Time(required=True)
        godzina_zamkniecia = graphene.Time(required=True)

    def mutate(self, info, kort_id, dzien_tygodnia, godzina_otwarcia, godzina_zamkniecia):
        kort = Kort.objects.get(pk=kort_id)
        godziny = GodzinyOtwarcia(
            kort=kort,
            dzien_tygodnia=dzien_tygodnia,
            godzina_otwarcia=godzina_otwarcia,
            godzina_zamkniecia=godzina_zamkniecia
        )
        godziny.save()
        return CreateGodzinyOtwarcia(godziny_otwarcia=godziny)


class UpdateGodzinyOtwarcia(graphene.Mutation):
    godziny_otwarcia = graphene.Field(GodzinyOtwarciaType)

    class Arguments:
        id = graphene.ID(required=True)
        dzien_tygodnia = graphene.String()
        godzina_otwarcia = graphene.Time()
        godzina_zamkniecia = graphene.Time()

    def mutate(self, info, id, dzien_tygodnia=None, godzina_otwarcia=None, godzina_zamkniecia=None):
        godziny = GodzinyOtwarcia.objects.get(pk=id)
        if dzien_tygodnia:
            godziny.dzien_tygodnia = dzien_tygodnia
        if godzina_otwarcia:
            godziny.godzina_otwarcia = godzina_otwarcia
        if godzina_zamkniecia:
            godziny.godzina_zamkniecia = godzina_zamkniecia
        godziny.save()
        return UpdateGodzinyOtwarcia(godziny_otwarcia=godziny)


class DeleteGodzinyOtwarcia(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        godziny = GodzinyOtwarcia.objects.get(pk=id)
        godziny.delete()
        return DeleteGodzinyOtwarcia(ok=True)


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_kort = CreateKort.Field()
    update_kort = UpdateKort.Field()
    delete_kort = DeleteKort.Field()

    create_godziny_otwarcia = CreateGodzinyOtwarcia.Field()
    update_godziny_otwarcia = UpdateGodzinyOtwarcia.Field()
    delete_godziny_otwarcia = DeleteGodzinyOtwarcia.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
