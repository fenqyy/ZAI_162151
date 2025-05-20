from django.db.models import Count
from rest_framework.generics import UpdateAPIView, CreateAPIView, DestroyAPIView, get_object_or_404, \
    RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from .models import Lokalizacja, Profil, Kort
from .serializers import UserSerializer, LokalizacjaSerializer, RezerwacjaSerializer


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocalizationView(APIView):
    permission_classes = []
    def get(self, request):
        lokalizacje = Lokalizacja.objects.annotate(ile_kortow=Count('kort'))
        serializer = LokalizacjaSerializer(lokalizacje, many=True)
        return Response(serializer.data)


class LocalizationUpdateView(RetrieveUpdateAPIView):
    permission_classes = []
    queryset = Lokalizacja.objects.all()
    serializer_class = LokalizacjaSerializer


class LocalizationDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = []
    queryset = Lokalizacja.objects.all()
    serializer_class = LokalizacjaSerializer


class LocalizationCreateView(generics.ListCreateAPIView):
    permission_classes = []
    queryset = Lokalizacja.objects.all()
    serializer_class = LokalizacjaSerializer


class ReservationView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RezerwacjaSerializer

    def get_serializer_context(self):
        lokalizacja = get_object_or_404(Lokalizacja,
                                        pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'],
                                 lokalizacja=lokalizacja)
        return {'kort': kort}

    def perform_create(self, serializer):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        profil = Profil.objects.get(user=self.request.user)
        serializer.save(kort=kort, profil=profil)



