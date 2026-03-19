from typing import List, Optional
from ninja import NinjaAPI, ModelSchema, Schema, FilterSchema, Field, File, Query
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Author, Book

api = NinjaAPI()

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


@api.post("/authors", response=AuthorSchema)
def create_author(request, payload: AuthorCreateSchema):
    author = Author.objects.create(**payload.dict())
    return author

@api.get("/authors", response=List[AuthorSchema])
def list_authors(request):
    return Author.objects.all()

@api.get("/authors/{author_id}", response=AuthorSchema)
def get_author(request, author_id: int):
    author = get_object_or_404(Author, id=author_id)
    return author

@api.put("/authors/{author_id}", response=AuthorSchema)
def update_author(request, author_id: int, payload: AuthorCreateSchema):
    author = get_object_or_404(Author, id=author_id)
    for attr, value in payload.dict().items():
        setattr(author, attr, value)
    author.save()
    return author

@api.delete("/authors/{author_id}")
def delete_author(request, author_id: int):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return {"success": True}


@api.post("/books", response=BookSchema)
def create_book(request, payload: BookCreateSchema):
    book = Book.objects.create(**payload.dict())
    return book

@api.get("/books", response=List[BookSchema])
def list_books(request, filters: BookFilterSchema = Query(...)):
    books = Book.objects.all()
    return filters.filter(books)

@api.get("/books/{book_id}", response=BookSchema)
def get_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    return book

@api.put("/books/{book_id}", response=BookSchema)
def update_book(request, book_id: int, payload: BookCreateSchema):
    book = get_object_or_404(Book, id=book_id)
    for attr, value in payload.dict().items():
        setattr(book, attr, value)
    book.save()
    return book

@api.delete("/books/{book_id}")
def delete_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return {"success": True}

@api.post("/books/{book_id}/cover")
def upload_book_cover(request, book_id: int, file: UploadedFile = File(...)):
    book = get_object_or_404(Book, id=book_id)
    book.cover.save(file.name, file)
    return {"success": True, "cover_url": book.cover.url}
