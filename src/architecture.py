from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle


OUTPUT_FILE = Path("assets/arquitetura_api_final.png")


def add_card(ax, x, y, w, h, title, subtitle, color, icon="", fontsize=10):
    card = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.08",
        linewidth=0,
        facecolor=color,
        edgecolor=color,
    )
    ax.add_patch(card)

    if icon:
        ax.text(
            x + 0.42,
            y + h / 2,
            icon,
            ha="center",
            va="center",
            fontsize=30,
            color="white",
            fontweight="bold",
        )
        text_x = x + 0.9
        ha = "left"
    else:
        text_x = x + w / 2
        ha = "center"

    ax.text(
        text_x,
        y + h * 0.58,
        title,
        ha=ha,
        va="center",
        fontsize=fontsize,
        color="white",
        fontweight="bold",
    )

    ax.text(
        text_x,
        y + h * 0.36,
        subtitle,
        ha=ha,
        va="center",
        fontsize=fontsize - 1,
        color="white",
        fontweight="bold",
    )


def add_arrow(ax, x1, y1, x2, y2, connectionstyle="arc3,rad=0"):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>",
            mutation_scale=22,
            linewidth=2.2,
            color="#0B2545",
            shrinkA=2,
            shrinkB=2,
            connectionstyle=connectionstyle,
        ),
    )


def add_layer_title(ax, y, text):
    ax.text(
        0.45,
        y,
        text,
        ha="left",
        va="center",
        fontsize=15,
        color="#0B2545",
        fontweight="bold",
    )


def add_dotted_line(ax, y):
    ax.plot(
        [0.45, 16.7],
        [y, y],
        linestyle=(0, (2, 3)),
        linewidth=1.5,
        color="#CBD5E1",
    )


def add_footer(ax):
    footer = FancyBboxPatch(
        (1.8, 0.65),
        13.6,
        0.95,
        boxstyle="round,pad=0.08",
        linewidth=1.3,
        facecolor="#FFFFFF",
        edgecolor="#CBD5E1",
    )
    ax.add_patch(footer)

    circle = Circle(
        (2.55, 1.12),
        0.34,
        facecolor="#1E88E5",
        edgecolor="#1E88E5",
    )
    ax.add_patch(circle)

    ax.text(
        2.55,
        1.12,
        "💡",
        ha="center",
        va="center",
        fontsize=22,
        color="white",
    )

    ax.text(
        3.25,
        1.25,
        "Fluxo:",
        ha="left",
        va="center",
        fontsize=12,
        color="#0B2545",
        fontweight="bold",
    )

    ax.text(
        4.0,
        1.25,
        "os dados são coletados da Amazon, tratados e armazenados em JSON.",
        ha="left",
        va="center",
        fontsize=11,
        color="#0B2545",
        fontweight="bold",
    )

    ax.text(
        3.25,
        0.95,
        (
            "A API FastAPI disponibiliza os dados e sua documentação. "
            "A análise descritiva consome a própria API com Requests,"
        ),
        ha="left",
        va="center",
        fontsize=10.5,
        color="#0B2545",
        fontweight="bold",
    )

    ax.text(
        3.25,
        0.72,
        (
            "processa os dados com Pandas e gera gráficos com Matplotlib "
            "para compor a visão analítica dos best sellers."
        ),
        ha="left",
        va="center",
        fontsize=10.5,
        color="#0B2545",
        fontweight="bold",
    )


def add_legend(ax):
    items = [
        ("#1E88E5", "Fonte / Consumo"),
        ("#16A34A", "Processamento"),
        ("#F59E0B", "Transformação / Visualização"),
        ("#8E24AA", "API / Documentação"),
        ("#E53935", "Resultado"),
    ]

    x = 3.25
    y = 0.22

    for color, label in items:
        ax.scatter(x, y, s=120, color=color)
        ax.text(
            x + 0.3,
            y,
            label,
            ha="left",
            va="center",
            fontsize=10,
            color="#0B2545",
        )
        x += 2.7


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_xlim(0, 17.2)
    ax.set_ylim(0, 10)
    ax.axis("off")

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.text(
        8.6,
        9.55,
        "Arquitetura da API - Amazon Best Sellers Books",
        ha="center",
        va="center",
        fontsize=28,
        color="#0B2545",
        fontweight="bold",
    )

    blue = "#1E88E5"
    green = "#16A34A"
    orange = "#F59E0B"
    purple = "#8E24AA"
    red = "#E53935"

    add_layer_title(ax, 8.9, "1. Ingestão e Armazenamento")

    add_card(
        ax, 1.05, 7.55, 2.6, 0.95,
        "Amazon Best", "Sellers Books",
        blue, icon="a", fontsize=11
    )

    add_card(
        ax, 4.4, 7.55, 3.15, 0.95,
        "Scraper Python", "Selenium + BeautifulSoup",
        green, icon="</>", fontsize=11
    )

    add_card(
        ax, 8.25, 7.55, 3.2, 0.95,
        "Tratamento dos Dados", "Título, Autor, Preço e Avaliação",
        orange, icon="▽", fontsize=10
    )

    add_card(
        ax, 12.35, 7.55, 2.75, 0.95,
        "Base Tratada", "books.json",
        purple, icon="◎", fontsize=11
    )

    add_arrow(ax, 3.65, 8.02, 4.4, 8.02)
    add_arrow(ax, 7.55, 8.02, 8.25, 8.02)
    add_arrow(ax, 11.45, 8.02, 12.35, 8.02)

    add_dotted_line(ax, 6.95)

    add_layer_title(ax, 6.55, "2. API e Documentação")

    add_card(
        ax, 7.9, 5.35, 2.95, 1.0,
        "REST API", "FastAPI",
        blue, icon="🚀", fontsize=12
    )

    add_card(
        ax, 4.05, 5.35, 3.0, 1.0,
        "Endpoints", "/books\n/analytics\n/health",
        green, icon="▦", fontsize=11
    )

    add_card(
        ax, 11.95, 5.35, 3.05, 1.0,
        "Swagger", "Documentação\n/docs",
        purple, icon="▯", fontsize=11
    )

    add_arrow(
        ax, 13.72, 7.55, 9.38, 6.35,
        connectionstyle="angle3,angleA=-90,angleB=180"
    )

    add_arrow(ax, 7.9, 5.85, 7.05, 5.85)
    add_arrow(ax, 10.85, 5.85, 11.95, 5.85)

    add_dotted_line(ax, 4.7)

    add_layer_title(ax, 4.25, "3. Consumo da API e Visão Analítica")

    add_card(
        ax, 2.15, 3.0, 3.05, 0.95,
        "analysis.py", "Consome a API\nRequests",
        blue, icon="<>", fontsize=10
    )

    add_card(
        ax, 6.05, 3.0, 2.9, 0.95,
        "Análise Descritiva", "Pandas",
        green, icon="▥", fontsize=11
    )

    add_card(
        ax, 9.9, 3.0, 2.8, 0.95,
        "Visualização", "Matplotlib",
        orange, icon="⌁", fontsize=11
    )

    add_card(
        ax, 13.55, 3.0, 2.8, 0.95,
        "Visão Analítica", "Best Sellers",
        red, icon="◔", fontsize=11
    )

    add_arrow(
        ax, 9.38, 5.35, 3.67, 3.95,
        connectionstyle="angle3,angleA=-90,angleB=180"
    )

    add_arrow(ax, 5.2, 3.48, 6.05, 3.48)
    add_arrow(ax, 8.95, 3.48, 9.9, 3.48)
    add_arrow(ax, 12.7, 3.48, 13.55, 3.48)

    add_footer(ax)
    add_legend(ax)

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Arquitetura final salva em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()