import graphene
import graphql_jwt
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from korty.models import Lokalizacja, Kort

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class LokalizacjaType(DjangoObjectType):
    class Meta:
        model = Lokalizacja
        fields = ['id', 'miasto', 'adres', 'kod_pocztowy']

class KortType(DjangoObjectType):
    class Meta:
        model = Kort
        fields = ['id', 'nazwa', 'typ', 'lokalizacja']

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_lokalizacje = graphene.List(LokalizacjaType)

    def resolve_all_users(self, info):
        return User.objects.all()

    def resolve_all_lokalizacje(self, info):
        return Lokalizacja.objects.all()

class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = User(username=username)
        user.set_password(password)
        user.save()
        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    create_user = CreateUser.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
