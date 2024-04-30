from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserDetailsView,
    GenreAPIView,
    AnimeAPIView,
    AnimesAPIView,
    UserAnimeStatusAPIView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("getme/", UserDetailsView.as_view()),
    path("genres/", GenreAPIView.as_view()),
    path("animes/", AnimesAPIView.as_view()),
    path("anime/<str:pk>", AnimeAPIView.as_view()),
    path(
        "user-anime-status/", UserAnimeStatusAPIView.as_view(), name="user-anime-status"
    ),
]
