from typing import List, Optional
from ninja import NinjaAPI, ModelSchema, Schema, FilterSchema, Field, File, Query, Router, Form
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Author, Book, Film, Person, Studio, Review, FilmMedia
from ninja.pagination import paginate, LimitOffsetPagination, PageNumberPagination, CursorPagination

api = NinjaAPI()

author_router = Router(tags=["Авторы"])
book_router = Router(tags=["Книги"])
film_router = Router(tags=["Фильмы"])
person_router = Router(tags=["авторы фильмов"])


class AuthorSchema(ModelSchema):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'birth_date']

class AuthorCreateSchema(Schema):
    first_name: str
    last_name: str
    birth_date: str = None

class BookSchema(ModelSchema):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publication_year', 'summary', 'genre', 'rating', 'page_count', 'cover']

class BookCreateSchema(Schema):
    title: str
    author_id: int
    publication_year: int
    summary: str = None
    genre: str = 'другое'
    rating: int = 1
    page_count: int = 0

class BookFilterSchema(FilterSchema):
    title: Optional[str] = Field(None, q='title__icontains')
    year_from: Optional[int] = Field(None, q='publication_year__gte')
    year_to: Optional[int] = Field(None, q='publication_year__lte')
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    genre_types: Optional[List[str]] = Field(None, alias="type")
    rating: Optional[int] = Field(None, q='rating__gte')
    pages_from: Optional[int] = Field(None, q='page_count__gte')
    pages_to: Optional[int] = Field(None, q='page_count__lte')

    def filter_author_name(self, value: str) -> Q:
        return Q(author__first_name__icontains=value) | Q(author__last_name__icontains=value)

    def filter_genre_types(self, value: List[str]) -> Q:
        return Q(genre__in=value)

class FilmSchema(ModelSchema):
    class Meta:
        model = Film
        fields = ['id', 'title', 'release_year', 'studio']

    actors: List[int] = []
    directors: List[int] = []
    producers: List[int] = []

    @staticmethod
    def resolve_actors(obj):
        return list(obj.actors.values_list('id', flat=True))

    @staticmethod
    def resolve_directors(obj):
        return list(obj.directors.values_list('id', flat=True))

    @staticmethod
    def resolve_producers(obj):
        return list(obj.producers.values_list('id', flat=True))

class FilmCreateSchema(Schema):
    title: str
    release_year: int
    studio_id: int = None
    directors_ids: List[int] = []
    actors_ids: List[int] = []
    producers_ids: List[int] = []

class PersonSchema(ModelSchema):
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'biography', 'photo']

class PersonCreateSchema(Schema):
    first_name: str
    last_name: str
    birth_date: str = None
    biography: str = ""


#  Авторы

@author_router.post("/", response=AuthorSchema)
def create_author(request, payload: AuthorCreateSchema):
    author = Author.objects.create(**payload.dict())
    return author

@author_router.get("/", response=List[AuthorSchema])
def list_authors(request):
    return Author.objects.all()

@author_router.get("/{author_id}", response=AuthorSchema)
def get_author(request, author_id: int):
    return get_object_or_404(Author, id=author_id)

@author_router.put("/{author_id}", response=AuthorSchema)
def update_author(request, author_id: int, payload: AuthorCreateSchema):
    author = get_object_or_404(Author, id=author_id)
    for attr, value in payload.dict().items():
        setattr(author, attr, value)
    author.save()
    return author

@author_router.delete("/{author_id}")
def delete_author(request, author_id: int):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return {"success": True}


#Книги

@book_router.post("/", response=BookSchema)
def create_book(request, payload: BookCreateSchema):
    book = Book.objects.create(**payload.dict())
    return book

@book_router.get("/", response=List[BookSchema])
def list_books(request, filters: BookFilterSchema = Query(...)):
    books = Book.objects.all()
    return filters.filter(books)

# пагинация
@book_router.get("/limit", response=List[BookSchema])
@paginate(LimitOffsetPagination)
def list_books_limit(request):
    return Book.objects.all()

@book_router.get("/pages", response=List[BookSchema])
@paginate(PageNumberPagination, page_size=5)
def list_books_pages(request):
    return Book.objects.all()

@book_router.get("/cursor", response=List[BookSchema])
@paginate(CursorPagination, page_size=5, ordering=("id",))
def list_books_cursor(request):
    return Book.objects.all()

@book_router.get("/{book_id}", response=BookSchema)
def get_book(request, book_id: int):
    return get_object_or_404(Book, id=book_id)

@book_router.put("/{book_id}", response=BookSchema)
def update_book(request, book_id: int, payload: BookCreateSchema):
    book = get_object_or_404(Book, id=book_id)
    for attr, value in payload.dict().items():
        setattr(book, attr, value)
    book.save()
    return book

@book_router.delete("/{book_id}")
def delete_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return {"success": True}

@book_router.post("/{book_id}/cover")
def upload_book_cover(request, book_id: int, file: UploadedFile = File(...)):
    book = get_object_or_404(Book, id=book_id)
    book.cover.save(file.name, file)
    return {"success": True, "cover_url": book.cover.url}


# Фильмы

@film_router.get("/", response=List[FilmSchema])
def list_films(request):
    return Film.objects.all()

@film_router.get("/{film_id}", response=FilmSchema)
def get_film(request, film_id: int):
    return get_object_or_404(Film, id=film_id)

@film_router.post("/", response=FilmSchema)
def create_film(request, payload: FilmCreateSchema):
    data = payload.dict()
    directors_ids = data.pop('directors_ids')
    actors_ids = data.pop('actors_ids')
    producers_ids = data.pop('producers_ids')
    film = Film.objects.create(**data)
    film.directors.set(directors_ids)
    film.actors.set(actors_ids)
    film.producers.set(producers_ids)
    return film

@film_router.put("/{film_id}", response=FilmSchema)
def update_film(request, film_id: int, payload: FilmCreateSchema):
    film = get_object_or_404(Film, id=film_id)
    data = payload.dict()
    directors_ids = data.pop('directors_ids')
    actors_ids = data.pop('actors_ids')
    producers_ids = data.pop('producers_ids')
    for attr, value in data.items():
        setattr(film, attr, value)
    film.save()
    film.directors.set(directors_ids)
    film.actors.set(actors_ids)
    film.producers.set(producers_ids)
    return film

@film_router.delete("/{film_id}")
def delete_film(request, film_id: int):
    film = get_object_or_404(Film, id=film_id)
    film.delete()
    return {"success": True}


# Персоны (авторы фильмов)#

@person_router.get("/", response=List[PersonSchema])
def list_persons(request):
    return Person.objects.all()

@person_router.get("/{person_id}", response=PersonSchema)
def get_person(request, person_id: int):
    return get_object_or_404(Person, id=person_id)

@person_router.post("/", response=PersonSchema)
def create_person(request, payload: PersonCreateSchema = Form(...), photo: UploadedFile = File(None)):
    person = Person.objects.create(**payload.dict())
    if photo:
        person.photo.save(photo.name, photo)
    return person

@person_router.put("/{person_id}", response=PersonSchema)
def update_person(request, person_id: int, payload: PersonCreateSchema):
    person = get_object_or_404(Person, id=person_id)
    for attr, value in payload.dict().items():
        setattr(person, attr, value)
    person.save()
    return person

@person_router.delete("/{person_id}")
def delete_person(request, person_id: int):
    person = get_object_or_404(Person, id=person_id)
    person.delete()
    return {"success": True}

@person_router.post("/{person_id}/photo")
def upload_person_photo(request, person_id: int, file: UploadedFile = File(...)):
    person = get_object_or_404(Person, id=person_id)
    person.photo.save(file.name, file)
    return {"success": True, "photo_url": person.photo.url}


#Студии

class StudioSchema(ModelSchema):
    class Meta:
        model = Studio
        fields = ['id', 'name']

class StudioCreateSchema(Schema):
    name: str

studio_router = Router(tags=["Студии"])

@studio_router.get("/", response=List[StudioSchema])
def list_studios(request):
    return Studio.objects.all()

@studio_router.get("/{studio_id}", response=StudioSchema)
def get_studio(request, studio_id: int):
    return get_object_or_404(Studio, id=studio_id)

@studio_router.post("/", response=StudioSchema)
def create_studio(request, payload: StudioCreateSchema):
    return Studio.objects.create(**payload.dict())

@studio_router.put("/{studio_id}", response=StudioSchema)
def update_studio(request, studio_id: int, payload: StudioCreateSchema):
    studio = get_object_or_404(Studio, id=studio_id)
    studio.name = payload.name
    studio.save()
    return studio

@studio_router.delete("/{studio_id}")
def delete_studio(request, studio_id: int):
    studio = get_object_or_404(Studio, id=studio_id)
    studio.delete()
    return {"success": True}


# Рецензии

class ReviewSchema(ModelSchema):
    class Meta:
        model = Review
        fields = ['id', 'film', 'author_name', 'text', 'rating']

class ReviewCreateSchema(Schema):
    film_id: int
    author_name: str
    text: str
    rating: int = 1

review_router = Router(tags=["Рецензии"])

@review_router.get("/", response=List[ReviewSchema])
def list_reviews(request, film_id: Optional[int] = None):
    qs = Review.objects.all()
    if film_id:
        qs = qs.filter(film_id=film_id)
    return qs

@review_router.get("/{review_id}", response=ReviewSchema)
def get_review(request, review_id: int):
    return get_object_or_404(Review, id=review_id)

@review_router.post("/", response=ReviewSchema)
def create_review(request, payload: ReviewCreateSchema):
    return Review.objects.create(**payload.dict())

@review_router.put("/{review_id}", response=ReviewSchema)
def update_review(request, review_id: int, payload: ReviewCreateSchema):
    review = get_object_or_404(Review, id=review_id)
    for attr, value in payload.dict().items():
        setattr(review, attr, value)
    review.save()
    return review

@review_router.delete("/{review_id}")
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return {"success": True}


#Медиа фильмов

class FilmMediaSchema(ModelSchema):
    class Meta:
        model = FilmMedia
        fields = ['id', 'film', 'media_type', 'file']

media_router = Router(tags=["Медиа фильмов"])

@media_router.get("/", response=List[FilmMediaSchema])
def list_media(request, film_id: Optional[int] = None):
    qs = FilmMedia.objects.all()
    if film_id:
        qs = qs.filter(film_id=film_id)
    return qs

@media_router.get("/{media_id}", response=FilmMediaSchema)
def get_media(request, media_id: int):
    return get_object_or_404(FilmMedia, id=media_id)

@media_router.post("/", response=FilmMediaSchema)
def create_media(request, film_id: int = Form(...), media_type: str = Form(...), file: UploadedFile = File(...)):
    film = get_object_or_404(Film, id=film_id)
    media = FilmMedia(film=film, media_type=media_type)
    media.file.save(file.name, file)
    return media

@media_router.delete("/{media_id}")
def delete_media(request, media_id: int):
    media = get_object_or_404(FilmMedia, id=media_id)
    media.delete()
    return {"success": True}


#Регистрация роутеров

api.add_router("/authors", author_router)
api.add_router("/books", book_router)
api.add_router("/films", film_router)
api.add_router("/persons", person_router)
api.add_router("/studios", studio_router)
api.add_router("/reviews", review_router)
api.add_router("/media", media_router)
