from django.urls import path
from accounts.views import (
    FollowToggleView,

)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import RegisterView, ProfileView, ChangePasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile_detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', ProfileView.as_view(), name='me'),
path(
        'users/<int:user_id>/follow/',
        FollowToggleView.as_view(),
        name='follow_toggle',
    ),
path(
        'change-password/',
        ChangePasswordView.as_view(),
        name='change_password',
    ),
]