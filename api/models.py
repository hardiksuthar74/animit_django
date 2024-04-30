from django.db import models

from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Anime(models.Model):
    jikan_anime_id = models.IntegerField()
    image = models.CharField(max_length=1000)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    episodes = models.IntegerField(default=0)
    score = models.DecimalField(default=0, decimal_places=3, max_digits=4)
    scored_by = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    popularity = models.IntegerField(default=0)
    favorites = models.IntegerField(default=0)
    synopsis = models.CharField()
    background = models.CharField(blank=True, null=True)
    season = models.CharField(max_length=255)
    year = models.IntegerField()
    genres = models.ManyToManyField(Genre)


class UserAnimeStatus(models.Model):
    PROCESS_CHOICES = (
        (1, "Watchlist"),
        (2, "Watching"),
        (3, "Completed"),
        (4, "On Hold"),
        (5, "Dropped"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    process = models.IntegerField(choices=PROCESS_CHOICES)
    episodes = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "anime")
