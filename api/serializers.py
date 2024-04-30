# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Anime, Genre, UserAnimeStatus


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class AnimeSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Anime
        fields = "__all__"


class SeeAnimeSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Anime
        fields = "__all__"


class UserAnimeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnimeStatus
        fields = ["id", "user", "anime", "process", "episodes"]


class UserSeeAnimeStatusSerializer(serializers.ModelSerializer):
    anime = (
        serializers.SerializerMethodField()
    )  # Use SerializerMethodField for custom representation

    class Meta:
        model = UserAnimeStatus
        fields = ["id", "user", "anime", "process", "episodes"]

    def get_anime(self, obj):
        anime_obj = Anime.objects.get(id=obj.anime_id)
        anime_data = {
            "id": anime_obj.id,
            "title": anime_obj.title,
            "image": anime_obj.image,
        }
        return anime_data
