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
        FANTASY = 'фэнтези', 'Фэнтези'
        SCIFI = 'фантастика', 'Фантастика'
        OTHER = 'другое', 'Другое'

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
