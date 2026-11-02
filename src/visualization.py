import base64
from io import BytesIO
from pathlib import Path
from typing import Mapping, Sequence

import folium
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def create_crime_map(
    default_location: tuple[float, float] = (-23.550520, -46.633308),
) -> folium.Map:
    return folium.Map(location=default_location, zoom_start=12)


def add_crime_marker(
    crime_map: folium.Map,
    lat: float,
    lon: float,
    bairro: str,
    data: str,
    hora: str,
) -> None:
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>Bairro:</b> {bairro}<br><b>Data:</b> {data}<br><b>Hora:</b> {hora}",
        tooltip="Clique para mais detalhes",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(crime_map)


def generate_sentiment_chart(
    sentimentos_roubo: Sequence[Mapping[str, float]],
    sentimentos_policiamento: Sequence[Mapping[str, float]],
    output_html: str | Path = DEFAULT_OUTPUT_DIR / "grafico_sentimentos.html",
) -> None:
    scores_roubo = [sentiment["compound"] for sentiment in sentimentos_roubo]
    scores_policiamento = [
        sentiment["compound"] for sentiment in sentimentos_policiamento
    ]

    plt.figure(figsize=(10, 5))
    if scores_roubo:
        plt.bar(
            range(len(scores_roubo)),
            scores_roubo,
            label="Roubo",
            color="red",
            alpha=0.7,
        )
    if scores_policiamento:
        plt.bar(
            range(len(scores_roubo), len(scores_roubo) + len(scores_policiamento)),
            scores_policiamento,
            label="Policiamento",
            color="blue",
            alpha=0.7,
        )
    if not scores_roubo and not scores_policiamento:
        plt.text(0.5, 0.5, "Nenhum sentimento registrado", ha="center", va="center")
        plt.xlim(0, 1)
        plt.ylim(0, 1)

    plt.xlabel("Índice da Mensagem")
    plt.ylabel("Score de Sentimento (Compound)")
    plt.title("Análise de Sentimento dos Posts")
    if scores_roubo or scores_policiamento:
        plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    tmpfile = BytesIO()
    plt.savefig(tmpfile, format="png", bbox_inches="tight")
    encoded = base64.b64encode(tmpfile.getvalue()).decode("utf-8")
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Análise de Sentimentos</title></head>
<body><img alt="Gráfico de análise de sentimentos" src="data:image/png;base64,{encoded}"></body>
</html>"""

    output_path = Path(output_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        file.write(html)
    plt.close()
