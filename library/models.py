from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    class GenreChoices(models.TextChoices):
        DETECTIVE = 'детектив', 'Детектив'
        ROMANCE = 'роман', 'Роман'
        FANTASY = 'фэнтези', 'Фэнтези',
        SCIFI = 'фантастика', 'Фантастика'
        OTHER = 'другое', 'Другое'
        FIGTHING = "боевик", "Боевик"

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    publication_year = models.IntegerField()
    summary = models.TextField(blank=True)
    genre = models.CharField(max_length=50, choices=GenreChoices.choices, default=GenreChoices.OTHER)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    page_count = models.IntegerField(default=0)
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)

    def __str__(self):
        return self.title


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    photo = models.ImageField(upload_to='persons/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Studio(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Film(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    studio = models.ForeignKey(Studio, on_delete=models.SET_NULL, null=True, blank=True)
    actors = models.ManyToManyField(Person,related_name='acted_films', blank=True)
    directors = models.ManyToManyField(Person,related_name='directed_films', blank=True)
    producers = models.ManyToManyField(Person,related_name='produced_films', blank=True)
    
    def __str__(self):
        return self.title

class FilmMedia(models.Model):
    class MediaType(models.TextChoices):
        TRAILER = 'трейлер', 'Трейлер'
        FULL_MOVIE = 'movie', 'Полный фильм'
        IMAGE = 'image', 'Изображение'
        
    film = models.ForeignKey(Film,related_name='media_files', on_delete=models.CASCADE)
    media_type = models.CharField(max_length = 20,choices=MediaType.choices)

    file = models.FileField(upload_to='film_media/')


class Review(models.Model):
    film = models.ForeignKey(Film, related_name='reviews', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return f"Рецензия на {self.film.title} от {self.author_name}"
    