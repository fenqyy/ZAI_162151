from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserDetailView, UserListView, UserUpdateView, UserRegisterView, LocalizationView, \
    LocalizationUpdateView, LocalizationDeleteView, LocalizationCreateView, ReservationView

urlpatterns = [
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='test'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('register/', UserRegisterView.as_view(), name='user-create'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('lokalizacje/', LocalizationView.as_view(), name='lokalizacje'),
    path('lokalizacje/<int:pk>/update/', LocalizationUpdateView.as_view(), name='localization-update'),
    path('lokalizacje/<int:pk>/delete/', LocalizationDeleteView.as_view(), name='localization-delete'),
    path('lokalizacje/create/', LocalizationCreateView.as_view(), name='localization-create'),
    path('lokalizacje/<int:lokalizacja_pk>/korty/<int:kort_pk>/rezerwacje/dodaj/', ReservationView.as_view(),
         name='reservation-create')
]
