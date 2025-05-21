from django.db.models import Count
from rest_framework.generics import UpdateAPIView, CreateAPIView, DestroyAPIView, get_object_or_404, \
    RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User

from .models import Lokalizacja, Profil, Kort, Wydarzenia, Rezerwacja
from .serializers import UserSerializer, LokalizacjaSerializer, RezerwacjaSerializer, WydarzeniaSerializer


class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]

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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        lokalizacje = Lokalizacja.objects.annotate(ile_kortow=Count('kort'))
        serializer = LokalizacjaSerializer(lokalizacje, many=True)
        return Response(serializer.data)


class LocalizationUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Lokalizacja.objects.all()
    serializer_class = LokalizacjaSerializer


class LocalizationDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Lokalizacja.objects.all()
    serializer_class = LokalizacjaSerializer


class LocalizationCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Lokalizacja.objects.all()
    serializer_class = LokalizacjaSerializer


class ReservationListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Rezerwacja.objects.all()
    serializer_class = RezerwacjaSerializer
    search_fields = ['data']


class ReservationView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RezerwacjaSerializer

    def get_serializer_context(self):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        return {'kort': kort}

    def perform_create(self, serializer):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        profil = Profil.objects.get(user=self.request.user)
        serializer.save(kort=kort, profil=profil)


class EditReservationView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Rezerwacja.objects.all()
    serializer_class = RezerwacjaSerializer

    def get_serializer_context(self):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        return {'kort': kort}

    def get_queryset(self):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        return Rezerwacja.objects.filter(kort=kort)


class DeleteReservationView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Rezerwacja.objects.all()
    serializer_class = RezerwacjaSerializer

    def get_serializer_context(self):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        return {'kort': kort}

    def get_queryset(self):
        lokalizacja = get_object_or_404(Lokalizacja, pk=self.kwargs['lokalizacja_pk'])
        kort = get_object_or_404(Kort, pk=self.kwargs['kort_pk'], lokalizacja=lokalizacja)
        return Rezerwacja.objects.filter(kort=kort)

class EventView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Wydarzenia.objects.annotate(ile_uczestnikow=Count('uczestnicy'))
    serializer_class = WydarzeniaSerializer


class EditEventView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Wydarzenia.objects.all()
    serializer_class = WydarzeniaSerializer


class JoinEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        wydarzenie = get_object_or_404(Wydarzenia, pk=pk)
        profil = get_object_or_404(Profil, user=request.user)

        if wydarzenie.uczestnicy.filter(pk=profil.pk).exists():
            return Response({"detail": "Jesteś już zapisany na to wydarzenie."}, status=status.HTTP_400_BAD_REQUEST)

        wydarzenie.uczestnicy.add(profil)
        return Response({"detail": "Zapisano na wydarzenie."}, status=status.HTTP_200_OK)


class CreateEventView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Wydarzenia.objects.all()
    serializer_class = WydarzeniaSerializer