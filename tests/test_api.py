from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["total_books"] == 100


def test_get_books_limit():
    response = client.get("/books?limit=5")

    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 5
    assert len(data["books"]) == 5


def test_get_book_by_rank():
    response = client.get("/books/1")

    data = response.json()

    assert response.status_code == 200
    assert data["rank"] == 1
    assert "title" in data
    assert "author" in data
    assert "price" in data
    assert "rating" in data


def test_search_books_by_author():
    response = client.get("/books/search?author=Elle%20Kennedy")

    data = response.json()

    assert response.status_code == 200
    assert data["total"] >= 1


def test_analytics_summary():
    response = client.get("/analytics/summary")

    data = response.json()

    assert response.status_code == 200
    assert data["total_books"] == 100
    assert data["books_with_price"] == 100
    assert "average_price" in data
    assert "average_rating" in data