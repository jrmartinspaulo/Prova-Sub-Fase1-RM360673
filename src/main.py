import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query


DATA_FILE = Path("data/processed/books.json")


app = FastAPI(
    title="Amazon Best Sellers Books API",
    description="API para consulta e análise dos livros best sellers da Amazon.",
    version="1.0.0",
)


def load_books() -> list[dict]:
    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Arquivo books.json não encontrado. Execute o scraper primeiro."
        )

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {
        "message": "Bem-vindo à Amazon Best Sellers Books API",
        "documentation": "/docs",
        "health_check": "/health",
        "books_endpoint": "/books",
        "analytics_summary": "/analytics/summary",
    }


@app.get("/health")
def health_check():
    books = load_books()

    return {
        "status": "ok",
        "total_books": len(books),
        "data_source": str(DATA_FILE),
    }


@app.get("/books")
def get_books(
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    max_price: Optional[float] = Query(default=None, ge=0),
):
    books = load_books()

    if min_rating is not None:
        books = [
            book for book in books
            if book.get("rating_numeric") is not None
            and book["rating_numeric"] >= min_rating
        ]

    if max_price is not None:
        books = [
            book for book in books
            if book.get("price_numeric") is not None
            and book["price_numeric"] <= max_price
        ]

    if limit is not None:
        books = books[:limit]

    return {
        "total": len(books),
        "books": books,
    }


# SEARCH VEM ANTES DO /books/{rank}
@app.get("/books/search")
def search_books(
    title: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
):
    books = load_books()

    if not title and not author:
        raise HTTPException(
            status_code=400,
            detail="Informe pelo menos um parâmetro: title ou author."
        )

    results = books

    if title:
        results = [
            book for book in results
            if title.lower() in book["title"].lower()
        ]

    if author:
        results = [
            book for book in results
            if author.lower() in book["author"].lower()
        ]

    return {
        "total": len(results),
        "results": results,
    }


@app.get("/books/{rank}")
def get_book_by_rank(rank: int):
    books = load_books()

    for book in books:
        if book["rank"] == rank:
            return book

    raise HTTPException(
        status_code=404,
        detail=f"Livro com rank {rank} não encontrado."
    )


@app.get("/analytics/summary")
def analytics_summary():
    books = load_books()

    prices = [
        book["price_numeric"]
        for book in books
        if book.get("price_numeric") is not None
    ]

    ratings = [
        book["rating_numeric"]
        for book in books
        if book.get("rating_numeric") is not None
    ]

    return {
        "total_books": len(books),
        "books_with_price": len(prices),
        "books_with_rating": len(ratings),
        "average_price": round(sum(prices) / len(prices), 2),
        "min_price": round(min(prices), 2),
        "max_price": round(max(prices), 2),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "min_rating": round(min(ratings), 2),
        "max_rating": round(max(ratings), 2),
    }


@app.get("/analytics/top-rated")
def top_rated_books(
    limit: int = Query(default=10, ge=1, le=100)
):
    books = load_books()

    valid_books = [
        book for book in books
        if book.get("rating_numeric") is not None
    ]

    sorted_books = sorted(
        valid_books,
        key=lambda book: book["rating_numeric"],
        reverse=True
    )

    return {
        "total": min(limit, len(sorted_books)),
        "books": sorted_books[:limit],
    }


@app.get("/analytics/price-stats")
def price_stats():
    books = load_books()

    valid_books = [
        book for book in books
        if book.get("price_numeric") is not None
    ]

    cheapest = min(
        valid_books,
        key=lambda book: book["price_numeric"]
    )

    most_expensive = max(
        valid_books,
        key=lambda book: book["price_numeric"]
    )

    return {
        "cheapest_book": cheapest,
        "most_expensive_book": most_expensive,
    }


@app.get("/analytics/authors")
def author_summary():
    books = load_books()

    author_count = {}

    for book in books:
        author = book.get("author", "N/A")

        if author != "N/A":
            author_count[author] = (
                author_count.get(author, 0) + 1
            )

    sorted_authors = sorted(
        author_count.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return {
        "total_authors": len(author_count),
        "authors": [
            {
                "author": author,
                "total_books": total
            }
            for author, total in sorted_authors
        ],
    }