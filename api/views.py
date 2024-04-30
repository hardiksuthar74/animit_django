# views.py
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    UserSerializer,
    AnimeSerializer,
    GenreSerializer,
    SeeAnimeSerializer,
    UserAnimeStatusSerializer,
    UserSeeAnimeStatusSerializer,
)
from .utils import ApiResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Anime, Genre, UserAnimeStatus
import requests

apiResponse = ApiResponse()


class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return apiResponse.successResponse(
                    serializer.data,
                    "User created successfully",
                    status=status.HTTP_201_CREATED,
                )
            return apiResponse.errorResponse(
                makeErrors(serializer.errors),
                "Invalid Fields",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(f"Login Error: {e}")
            return apiResponse.someThingWentWrong()


class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            errors = []
            if not username:
                errors.append({"key": "username", "message": "This field is required."})
            if not password:
                errors.append({"key": "password", "message": "This field is required."})
            if not username or not password:
                return apiResponse.errorResponse(
                    errors, "Invalid Fields", status=status.HTTP_400_BAD_REQUEST
                )
            user = authenticate(username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                response_data = {
                    "username": user.get_username(),
                    "token": token.key,
                }
                if created:
                    return apiResponse.successResponse(
                        response_data, "Welcome Back", status.HTTP_200_OK
                    )
                else:
                    return apiResponse.successResponse(
                        response_data, "Welcome Back", status.HTTP_200_OK
                    )

            else:
                return apiResponse.errorResponse(
                    None, "Invalid credentials", status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            print(f"Login Error: {e}")
            return apiResponse.someThingWentWrong()


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            user_data = {
                "username": user.username,
                "email": user.email,
            }
            return apiResponse.successResponse(
                user_data, f"Welcome Back {user.username}", status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Login Error: {e}")
            return apiResponse.someThingWentWrong()

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return apiResponse.errorResponse(
                None,
                "Authentication credentials were not provided.",
                status=status.HTTP_403_FORBIDDEN,
            )
        if isinstance(exc, AuthenticationFailed):
            return apiResponse.errorResponse(
                None,
                "Invalid Token",
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)


class GenreAPIView(APIView):
    def get(self, request):

        url = "https://api.jikan.moe/v4/genres/anime"
        response = requests.get(url)
        data = response.json()
        genres = data["data"]

        for genre_data in genres:
            genre_name = genre_data["name"]
            genre_obj, created = Genre.objects.get_or_create(name=genre_name)

        genres_queryset = Genre.objects.all()
        serializer = GenreSerializer(genres_queryset, many=True)
        return Response(serializer.data)


class AnimesAPIView(APIView):
    def get(self, request):
        queryset = Anime.objects.prefetch_related("genres")
        animes = SeeAnimeSerializer(queryset, many=True).data
        return Response(animes)


class AnimeAPIView(APIView):
    def get(self, request, pk):
        try:
            jikan_anime_id = pk
            if not jikan_anime_id:
                return Response({"error": "Please provide the anime ID"}, status=400)

            anime = Anime.objects.get(jikan_anime_id=jikan_anime_id)
            serializer = AnimeSerializer(anime)
            return Response(serializer.data, status=201)
        except Anime.DoesNotExist:
            url = f"https://api.jikan.moe/v4/anime/{pk}"
            response = requests.get(url)
            if response.status_code != 200:
                return Response(
                    {"error": "Failed to fetch anime details from Jikan API"},
                    status=response.status_code,
                )
            data = response.json()
            anime = data["data"]
            genre_ids = []

            for genre in anime.get("genres"):
                genre_id = Genre.objects.get(name=genre["name"])
                genreSerializer = GenreSerializer(genre_id)
                genre_ids.append(genreSerializer.data["id"])

            mainData = {
                "jikan_anime_id": anime["mal_id"],
                "title": anime.get("title"),
                "description": anime.get("synopsis"),
                "genres": genre_ids,
                "rating": anime.get("score"),
                "episodes": anime.get("episodes") or 0,
                "type": anime.get("type"),
                "synopsis": anime.get("synopsis"),
                "background": anime.get("background"),
                "season": anime.get("season"),
                "year": anime.get("year"),
                "image": anime["images"]["webp"]["large_image_url"],
            }

            serializer = AnimeSerializer(data=mainData)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)


class UserAnimeStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_anime_statuses = UserAnimeStatus.objects.filter(user=request.user)
        serializer = UserSeeAnimeStatusSerializer(user_anime_statuses, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            user_id = request.user.id
            jikan_anime_id = request.data.get("jikan_anime_id")
            process = request.data.get("process", 1)
            episodes = request.data.get("episodes", 0)

            if not jikan_anime_id:
                return Response(
                    {"error": "Please provide the anime ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            anime = Anime.objects.filter(jikan_anime_id=jikan_anime_id).first()

            if not anime:
                anime_data = fetch_anime_details(jikan_anime_id)
                anime_serializer = AnimeSerializer(data=anime_data)
                anime_serializer.is_valid(raise_exception=True)
                anime = anime_serializer.save()

            user_anime_status, created = UserAnimeStatus.objects.get_or_create(
                user_id=user_id,
                anime=anime,
                defaults={"process": process, "episodes": episodes},
            )

            if not created:
                user_anime_status.process = process
                user_anime_status.episodes = episodes
                user_anime_status.save()

            serializer = UserAnimeStatusSerializer(user_anime_status)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def fetch_anime_details(self, jikan_anime_id):
    url = f"https://api.jikan.moe/v4/anime/{jikan_anime_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to fetch anime details from Jikan API")

    anime_data = response.json()["data"]
    return extract_anime_data(anime_data)


def extract_anime_data(self, anime_data):
    return {
        "jikan_anime_id": anime_data["mal_id"],
        "title": anime_data.get("title"),
        "description": anime_data.get("synopsis"),
        "genres": [genre["name"] for genre in anime_data.get("genres", [])],
        "rating": anime_data.get("score"),
        "episodes": anime_data.get("episodes", 0),
        "type": anime_data.get("type"),
        "synopsis": anime_data.get("synopsis"),
        "background": anime_data.get("background"),
        "season": anime_data.get("season"),
        "year": anime_data.get("year"),
        "image": anime_data["images"]["webp"]["large_image_url"],
    }


def makeErrors(errors):
    error_array = []
    for key, value in errors.items():
        error_array.append({"key": key, "message": value[0]})
    return error_array
