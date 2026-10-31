import base64
from io import BytesIO
import matplotlib.pyplot as plt
import folium

def create_crime_map(default_location=[-23.550520, -46.633308]) -> folium.Map:
    return folium.Map(location=default_location, zoom_start=12)

def add_crime_marker(mapa: folium.Map, lat: float, lon: float, bairro: str, data: str, hora: str):
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>Bairro:</b> {bairro}<br><b>Data:</b> {data}<br><b>Hora:</b> {hora}",
        tooltip="Clique para mais detalhes",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(mapa)

def generate_sentiment_chart(sentimentos_roubo: list, sentimentos_policiamento: list, output_html: str = "output/grafico_sentimentos.html"):
    scores_roubo = [s['compound'] for s in sentimentos_roubo]
    scores_policiamento = [s['compound'] for s in sentimentos_policiamento]

    plt.figure(figsize=(10, 5))
    plt.bar(range(len(scores_roubo)), scores_roubo, label='Roubo', color='red')
    plt.bar(range(len(scores_roubo), len(scores_roubo) + len(scores_policiamento)), scores_policiamento, label='Policiamento', color='green')
    plt.xlabel('Índice da Mensagem')
    plt.ylabel('Score de Sentimento (VADER)')
    plt.title('Análise de Sentimento dos Posts')
    plt.legend()

    tmpfile = BytesIO()
    plt.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    html = f"<img src='data:image/png;base64,{encoded}'>"
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    plt.close()
