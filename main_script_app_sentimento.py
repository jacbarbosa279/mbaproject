import base64
from io import BytesIO
import os
from pathlib import Path
import webbrowser
import folium
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import time
from openai import APIError, OpenAI
from nltk.sentiment import SentimentIntensityAnalyzer

OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"
BASE_DIR = Path(__file__).resolve().parent
CAMINHO_DADOS = BASE_DIR / "data" / "raw" / "VeiculosSubtraidos_2024.xlsx"
CAMINHO_MENSAGENS = BASE_DIR / "mensagens_geradas.txt"
CAMINHO_MENSAGENS_PROCESSADAS = BASE_DIR / "data" / "processed" / "mensagens_geradas.txt"
CAMINHO_GRAFICO = BASE_DIR / "grafico_sentimentos.html"
CAMINHO_MAPA = BASE_DIR / "mapa_crimes.html"

# Baixa os recursos necessários para o NLTK
nltk.download('vader_lexicon')

# Inicializa o analisador de sentimentos do NLTK
sia = SentimentIntensityAnalyzer()


def criar_cliente_llm():
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "OPENROUTER_API_KEY não configurada. "
            "As mensagens serão criadas localmente, sem usar a API."
        )
        return None

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )


def gerar_mensagem(client, prompt, alternativa_local, index, tipo):
    if client is None:
        return alternativa_local

    try:
        completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        mensagem = completion.choices[0].message.content
        if mensagem and mensagem.strip():
            return mensagem.strip()
        raise ValueError("A API retornou uma mensagem vazia.")
    except (APIError, IndexError, ValueError) as error:
        print(
            f"Erro da API ao gerar {tipo} na linha {index}: {error}. "
            "Será usada uma mensagem local."
        )
        return alternativa_local


def main():
    client = criar_cliente_llm()

    # Carrega os dados do arquivo Excel
    df_roubos = pd.read_excel(CAMINHO_DADOS, sheet_name='AMOSTRAGEM')

    mapa = folium.Map(location=[-23.550520, -46.633308], zoom_start=12)

    sentimentos_roubo = []
    sentimentos_policiamento = []

    CAMINHO_MENSAGENS.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_MENSAGENS_PROCESSADAS.parent.mkdir(parents=True, exist_ok=True)
    with (
        open(CAMINHO_MENSAGENS, "w", encoding="utf-8", buffering=1) as arquivo_txt,
        open(
            CAMINHO_MENSAGENS_PROCESSADAS,
            "w",
            encoding="utf-8",
            buffering=1
        ) as arquivo_processado,
    ):

        for index, row in df_roubos.iterrows():
            tipo_crime = "roubo de veículo"
            bairro = row['BAIRRO']
            data_hora = row['DATA_OCORRENCIA_BO']
            hora = row['HORA_OCORRENCIA']
            tipo_carro = row['DESCR_TIPO_VEICULO']

            try:
                hora = pd.to_datetime(hora, format='%H:%M:%S')
                hora_formatada = hora.strftime('%H:%M:%S')
            except Exception:
                hora_formatada = "Sem informação"

            content = f"""Crie um post para as redes sociais alertando sobre um caso real de {tipo_crime} do {tipo_carro}
ocorrido no bairro de {bairro} 
no dia {data_hora.strftime('%d/%m/%Y')} às {hora_formatada}h.
Inclua hashtags relevantes."""

            try:
                alternativa_roubo = (
                    f"Alerta: foi registrado um {tipo_crime} de {tipo_carro} "
                    f"no bairro {bairro}, em {data_hora.strftime('%d/%m/%Y')} "
                    f"às {hora_formatada}. Redobre a atenção e acompanhe os "
                    "avisos dos canais oficiais. #Segurança #SãoPaulo"
                )
                post_roubo = gerar_mensagem(
                    client, content, alternativa_roubo, index, "post de roubo"
                )
                print(f"\n--- Post de Roubo (Linha {index}) ---\n{post_roubo}")
                registro_roubo = f"Post de roubo:\n{post_roubo}\n---\n"
                arquivo_txt.write(registro_roubo)
                arquivo_processado.write(registro_roubo)

                # Analisa sentimento
                sentimento_roubo = sia.polarity_scores(post_roubo)
                sentimentos_roubo.append(sentimento_roubo)
                print("Sentimento roubo:", sentimento_roubo)
                registro_sentimento_roubo = (
                    f"Sentimento do post de roubo: {sentimento_roubo}\n---\n"
                )
                arquivo_txt.write(registro_sentimento_roubo)
                arquivo_processado.write(registro_sentimento_roubo)
                
                # Força a gravação no disco imediatamente
                arquivo_txt.flush()

                # Define o prompt de policiamento com base no resultado
                if sentimento_roubo['compound'] < 0:
                    content_policiamento = f"""Crie uma mensagem positiva para as redes sociais 
elogiando o trabalho de policiamento no bairro {bairro}, 
apesar do {tipo_crime} ocorrido. 
Mencione que a polícia está trabalhando para garantir a segurança da comunidade."""
                else:
                    content_policiamento = f"""Crie uma mensagem positiva para as redes sociais 
sobre o trabalho de policiamento no bairro {bairro}. 
Mencione que a polícia está presente e atuante na região, 
contribuindo para a segurança da comunidade."""

                alternativa_policiamento = (
                    f"Informação para a comunidade do bairro {bairro}: "
                    "acompanhe os canais oficiais para atualizações sobre "
                    "segurança e procure os serviços de emergência quando "
                    "necessário. #Segurança #Comunidade"
                )
                post_policiamento = gerar_mensagem(
                    client,
                    content_policiamento,
                    alternativa_policiamento,
                    index,
                    "post de policiamento",
                )
                print(f"--- Post Policiamento ---\n{post_policiamento}")
                registro_policiamento = (
                    f"Post de policiamento:\n{post_policiamento}\n---\n"
                )
                arquivo_txt.write(registro_policiamento)
                arquivo_processado.write(registro_policiamento)

                sentimento_policiamento = sia.polarity_scores(post_policiamento)
                sentimentos_policiamento.append(sentimento_policiamento)
                print("Sentimento policiamento:", sentimento_policiamento)
                registro_sentimento_policiamento = (
                    f"Sentimento do post de policiamento: "
                    f"{sentimento_policiamento}\n---\n"
                )
                arquivo_txt.write(registro_sentimento_policiamento)
                arquivo_processado.write(registro_sentimento_policiamento)
                
                # Força a gravação no disco imediatamente
                arquivo_txt.flush()

            except Exception as e:
                print(f"Erro ao processar a linha {index}: {e}")

            # Adiciona o marcador ao mapa folium
            latitude = row['LATITUDE']
            longitude = row['LONGITUDE']
            folium.Marker(
                location=[latitude, longitude],
                popup=f"<b>Bairro:</b> {row['BAIRRO']}<br><b>Data:</b> {data_hora.strftime('%d/%m/%Y')}<br><b>Hora:</b> {hora_formatada}",
                tooltip="Clique para mais detalhes",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(mapa)

            if client is not None:
                time.sleep(3)

    mapa.save(CAMINHO_MAPA)
    print(f"Mapa salvo em: {CAMINHO_MAPA}")

    # Gera e exibe o gráfico de sentimentos
    gerar_grafico_sentimentos(sentimentos_roubo, sentimentos_policiamento)
    print(f"Mensagens salvas em: {CAMINHO_MENSAGENS}")
    print(f"Cópia das mensagens salva em: {CAMINHO_MENSAGENS_PROCESSADAS}")
    print(f"Gráfico salvo em: {CAMINHO_GRAFICO}")


def gerar_grafico_sentimentos(sentimentos_roubo, sentimentos_policiamento):
    if not sentimentos_roubo and not sentimentos_policiamento:
        scores_roubo = []
        scores_policiamento = []
    else:
        scores_roubo = [s['compound'] for s in sentimentos_roubo]
        scores_policiamento = [s['compound'] for s in sentimentos_policiamento]

    plt.figure(figsize=(10, 5))
    if scores_roubo or scores_policiamento:
        plt.bar(range(len(scores_roubo)), scores_roubo, label='Roubo', color='red', alpha=0.7)
    if scores_policiamento:
        plt.bar(
            range(len(scores_roubo), len(scores_roubo) + len(scores_policiamento)),
            scores_policiamento,
            label='Policiamento',
            color='blue',
            alpha=0.7
        )
    if not scores_roubo and not scores_policiamento:
        plt.text(0.5, 0.5, 'Nenhum sentimento registrado', ha='center', va='center')
        plt.xlim(0, 1)
        plt.ylim(0, 1)
    plt.xlabel('Índice da Mensagem')
    plt.ylabel('Score de Sentimento (Compound)')
    plt.title('Análise de Sentimento dos Posts')
    if scores_roubo or scores_policiamento:
        plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    # Salva no arquivo HTML
    tmpfile = BytesIO()
    plt.savefig(tmpfile, format='png', bbox_inches='tight')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Análise de Sentimentos</title></head>
<body><img alt="Gráfico de análise de sentimentos" src="data:image/png;base64,{encoded}"></body>
</html>"""
    
    with open(CAMINHO_GRAFICO, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Gráfico salvo em {CAMINHO_GRAFICO}")
    plt.close()

    if not webbrowser.open(CAMINHO_GRAFICO.resolve().as_uri()):
        print("Não foi possível abrir o navegador automaticamente; abra o HTML pelo caminho acima.")


if __name__ == "__main__":
    main()