import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from ftfy import fix_text


BASE_URL = "https://www.amazon.com/gp/bestsellers/books"
AMAZON_BASE_URL = "https://www.amazon.com"
OUTPUT_FILE = Path("data/processed/books.json")
RAW_DIR = Path("data/raw")


def clean_text(value: str) -> str:
    if not value:
        return "N/A"

    value = fix_text(value)
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip() if value.strip() else "N/A"


def extract_price_numeric(price: str):
    if not price or price == "N/A":
        return None

    cleaned = price.replace("$", "").replace(",", "").strip()

    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_rating_numeric(rating: str):
    if not rating or rating == "N/A":
        return None

    match = re.search(r"(\d+(\.\d+)?)", rating)

    if match:
        return float(match.group(1))

    return None


def create_driver() -> webdriver.Edge:
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=en-US")

    return webdriver.Edge(options=options)


def scroll_until_loaded(driver: webdriver.Edge, page_number: int) -> None:
    print(f"Rolando página {page_number} até o final...")

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Scroll até final... aguardando carregamento...")
        time.sleep(5)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

    print("Scroll final de confirmação...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "div.p13n-sc-uncoverable-faceout"
    )

    print(f"Página {page_number}: {len(cards)} cards após carregamento final")


def get_rank(card, fallback_rank: int) -> int:
    rank_tag = card.select_one(".zg-bdg-text")

    if rank_tag:
        rank_text = clean_text(rank_tag.get_text()).replace("#", "")

        if rank_text.isdigit():
            return int(rank_text)

    return fallback_rank


def get_product_url(card) -> str:
    link = card.select_one("a.a-link-normal[href]")

    if not link:
        return "N/A"

    href = link.get("href", "")

    if not href:
        return "N/A"

    return urljoin(AMAZON_BASE_URL, href.split("/ref=")[0])


def get_title(card) -> str:
    img = card.select_one("img")

    if img:
        alt_title = clean_text(img.get("alt", ""))

        if alt_title != "N/A" and len(alt_title) > 3:
            return alt_title

    selectors = [
        "div._cDEzb_p13n-sc-css-line-clamp-2_EWgCb",
        "div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y",
        "a.a-link-normal span div",
    ]

    for selector in selectors:
        tag = card.select_one(selector)

        if tag:
            value = clean_text(tag.get_text(strip=True))

            if value != "N/A":
                return value

    return "N/A"


def get_author(card) -> str:
    selectors = [
        "a.a-size-small.a-link-child",
        "span.a-size-small.a-color-base",
        "div.a-row.a-size-small",
    ]

    for selector in selectors:
        tag = card.select_one(selector)

        if tag:
            value = clean_text(tag.get_text(strip=True))

            if value != "N/A":
                return value

    return "N/A"


def get_rating(card) -> str:
    tag = card.select_one("span.a-icon-alt")

    if tag:
        return clean_text(tag.get_text(strip=True))

    return "N/A"


def get_price(card) -> str:
    selectors = [
        "span._cDEzb_p13n-sc-price_3mJ9Z",
        "span.p13n-sc-price",
        "span.a-color-price",
    ]

    for selector in selectors:
        tag = card.select_one(selector)

        if tag:
            value = clean_text(tag.get_text(strip=True))

            if value != "N/A":
                return value

    return "N/A"


def title_looks_truncated(title: str) -> bool:
    if title == "N/A":
        return True

    suspicious_endings = [
        ",",
        " S",
        " Stud",
        " Compr",
        " Spell",
        " Ac",
        " Sk",
        " Lan",
        " Wor",
    ]

    return any(title.endswith(end) for end in suspicious_endings)


def fetch_full_title_from_product_page(driver: webdriver.Edge, product_url: str) -> str:
    if product_url == "N/A":
        return "N/A"

    try:
        driver.get(product_url)
        time.sleep(3)

        title_element = driver.find_element(By.ID, "productTitle")
        return clean_text(title_element.text)

    except NoSuchElementException:
        return "N/A"
    except Exception:
        return "N/A"


def parse_books_from_html(html: str, page_number: int) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.p13n-sc-uncoverable-faceout")

    print(f"Total de cards encontrados no HTML da página {page_number}: {len(cards)}")

    books = []

    for index, card in enumerate(cards, start=1):
        fallback_rank = ((page_number - 1) * 50) + index

        title = get_title(card)
        author = get_author(card)
        rating = get_rating(card)
        price = get_price(card)
        product_url = get_product_url(card)

        books.append({
            "rank": get_rank(card, fallback_rank),
            "title": title,
            "author": author,
            "rating": rating,
            "rating_numeric": extract_rating_numeric(rating),
            "price": price,
            "price_numeric": extract_price_numeric(price),
            "source_url": product_url,
        })

    return books


def scrape_page(driver: webdriver.Edge, page_number: int) -> list[dict]:
    url = f"{BASE_URL}/ref=zg_bs_pg_{page_number}_books?pg={page_number}"

    print("-" * 70)
    print(f"Acessando página {page_number}: {url}")

    driver.get(url)
    time.sleep(5)

    scroll_until_loaded(driver, page_number)

    html = driver.page_source

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = RAW_DIR / f"amazon_books_page_{page_number}.html"
    raw_file.write_text(html, encoding="utf-8")

    return parse_books_from_html(html, page_number)


def enrich_truncated_titles(driver: webdriver.Edge, books: list[dict]) -> list[dict]:
    print("-" * 70)
    print("Verificando títulos possivelmente truncados...")

    for book in books:
        if title_looks_truncated(book["title"]):
            print(f"Corrigindo título do rank {book['rank']}...")

            full_title = fetch_full_title_from_product_page(
                driver,
                book["source_url"]
            )

            if full_title != "N/A" and len(full_title) > len(book["title"]):
                book["title"] = full_title

    return books


def scrape_amazon_books() -> None:
    driver = create_driver()

    try:
        all_books = []

        for page_number in [1, 2]:
            all_books.extend(scrape_page(driver, page_number))

        unique_books = {}

        for book in all_books:
            unique_books[book["rank"]] = book

        final_books = sorted(
            unique_books.values(),
            key=lambda item: item["rank"]
        )

        final_books = enrich_truncated_titles(driver, final_books)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(
                final_books,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("-" * 70)
        print(f"Arquivo salvo em: {OUTPUT_FILE}")
        print(f"Total final coletado: {len(final_books)}")
        print("-" * 70)

        books_without_rating = [
            book for book in final_books
            if book["rating_numeric"] is None
        ]

        books_without_price = [
            book for book in final_books
            if book["price_numeric"] is None
        ]

        print(f"Livros sem avaliação numérica: {len(books_without_rating)}")
        print(f"Livros sem preço numérico: {len(books_without_price)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_amazon_books()