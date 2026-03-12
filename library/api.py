from typing import List
from ninja import NinjaAPI, ModelSchema, Schema
from django.shortcuts import get_object_or_404
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
        fields = ['id', 'title', 'author', 'publication_year', 'summary']

class BookCreateSchema(Schema):
    title: str
    author_id: int
    publication_year: int
    summary: str = ""

# --- Authors --- #

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

# --- Books --- #

@api.post("/books", response=BookSchema)
def create_book(request, payload: BookCreateSchema):
    book = Book.objects.create(**payload.dict())
    return book

@api.get("/books", response=List[BookSchema])
def list_books(request):
    return Book.objects.all()

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
