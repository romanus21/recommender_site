from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=200)
    movie_logo = models.ImageField(upload_to='', blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Rating(models.Model):
    class Meta:
        unique_together = (('user', 'movie'),)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MaxValueValidator(5),
                                                        MinValueValidator(0)])
