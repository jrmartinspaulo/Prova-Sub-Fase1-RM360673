from pathlib import Path

import requests
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


API_URL = "http://127.0.0.1:8000"
ASSETS_DIR = Path("assets")
SUMMARY_FILE = ASSETS_DIR / "analise_descritiva.txt"


def load_books() -> pd.DataFrame:
    print("Consumindo API...")

    response = requests.get(f"{API_URL}/books?limit=100")

    if response.status_code != 200:
        raise Exception(f"Erro ao consumir API: {response.status_code}")

    data = response.json()
    books = data["books"]

    df = pd.DataFrame(books)

    print(f"Livros carregados via API: {len(df)}")

    return df


def get_api_json(endpoint: str) -> dict:
    response = requests.get(f"{API_URL}{endpoint}")

    if response.status_code != 200:
        raise Exception(f"Erro ao consumir {endpoint}: {response.status_code}")

    return response.json()


def save_summary(df: pd.DataFrame) -> None:
    summary = get_api_json("/analytics/summary")
    authors_response = get_api_json("/analytics/authors")

    top_5 = df.sort_values("rank").head(5)[
        ["rank", "title", "author", "rating", "price"]
    ]

    top_authors = pd.DataFrame(authors_response["authors"]).head(10)

    text = f"""
ANÁLISE DESCRITIVA - AMAZON BEST SELLERS

Fonte da análise: dados consumidos pela REST API desenvolvida no projeto.

Total de livros analisados: {summary['total_books']}
Livros com preço informado: {summary['books_with_price']}
Livros com avaliação informada: {summary['books_with_rating']}

Preço médio: US$ {summary['average_price']:.2f}
Menor preço: US$ {summary['min_price']:.2f}
Maior preço: US$ {summary['max_price']:.2f}

Avaliação média: {summary['average_rating']:.2f}
Menor avaliação: {summary['min_rating']:.2f}
Maior avaliação: {summary['max_rating']:.2f}

TOP 5 BEST SELLERS

{top_5.to_string(index=False)}

AUTORES COM MAIS LIVROS

{top_authors.to_string(index=False)}

CONCLUSÃO

A análise foi realizada consumindo os endpoints da API FastAPI criada no projeto.
Os resultados indicam predominância de livros com avaliações elevadas, além da
presença recorrente de autores, séries e materiais educacionais entre os best sellers.
"""

    SUMMARY_FILE.write_text(text.strip(), encoding="utf-8")

    print(f"Resumo salvo em: {SUMMARY_FILE}")


def plot_top_10_books(df: pd.DataFrame) -> None:
    top_10 = df.sort_values("rank").head(10).copy()

    labels = (
        top_10["rank"].astype(str)
        + " - "
        + top_10["title"].str.slice(0, 35)
    )

    plt.figure(figsize=(12, 7))
    plt.barh(labels, top_10["price_numeric"])
    plt.xlabel("Preço (US$)")
    plt.ylabel("Livro")
    plt.title("Top 10 Best Sellers - Preço")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    output = ASSETS_DIR / "top_10_best_sellers_precos.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Gráfico salvo: {output}")


def plot_rating_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    plt.hist(df["rating_numeric"].dropna(), bins=8)
    plt.xlabel("Avaliação")
    plt.ylabel("Quantidade")
    plt.title("Distribuição das Avaliações")
    plt.tight_layout()

    output = ASSETS_DIR / "distribuicao_avaliacoes.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Gráfico salvo: {output}")


def plot_price_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    plt.hist(df["price_numeric"].dropna(), bins=12)
    plt.xlabel("Preço (US$)")
    plt.ylabel("Quantidade")
    plt.title("Distribuição dos Preços")
    plt.tight_layout()

    output = ASSETS_DIR / "distribuicao_precos.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Gráfico salvo: {output}")


def plot_top_authors() -> None:
    authors_response = get_api_json("/analytics/authors")
    df = pd.DataFrame(authors_response["authors"]).head(10)

    plt.figure(figsize=(12, 7))
    plt.barh(df["author"], df["total_books"])
    plt.xlabel("Quantidade de livros")
    plt.ylabel("Autor")
    plt.title("Autores com Mais Livros")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    output = ASSETS_DIR / "top_autores.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Gráfico salvo: {output}")


def main() -> None:
    print("Iniciando análise via API...")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_books()

    save_summary(df)
    plot_top_10_books(df)
    plot_rating_distribution(df)
    plot_price_distribution(df)
    plot_top_authors()

    print("Análise finalizada com sucesso.")


if __name__ == "__main__":
    main()