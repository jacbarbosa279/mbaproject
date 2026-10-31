import base64
from io import BytesIO
import os
import folium
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import time
from openai import OpenAI
from nltk.sentiment import SentimentIntensityAnalyzer

# Baixa os recursos necessários para o NLTK (apenas na primeira vez)
nltk.download('vader_lexicon')

# Inicializa o cliente da API do OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Inicializa o analisador de sentimentos do NLTK
sia = SentimentIntensityAnalyzer()


# Função para validar a mensagem (opcional, se você ainda precisar dela)
def validar_mensagem(mensagem):
    if mensagem.empty:  # Verifica se a Series está vazia
        return False
    campos_essenciais = ['BAIRRO', 'CIDADE', 'DATA_OCORRENCIA_BO',
                        'HORA_OCORRENCIA', 'LOGRADOURO',
                        'NUMERO_LOGRADOURO', 'FLAG_FLAGRANTE',
                        'FLAG_STATUS', 'FLAG_ATO_INFRACIONAL',
                        'DESCR_MARCA_VEICULO']
    for campo in campos_essenciais:
        if pd.isna(mensagem[campo]):
            return False
    return True


def main():  # Função principal para organizar o código
    # Carregue os dados do arquivo Excel
    df_roubos = pd.read_excel('VeiculosSubtraidos_2024.xlsx',
                            sheet_name='AMOSTRAGEM')

    # Crie o mapa folium ANTES do loop
    mapa = folium.Map(location=[-23.550520, -46.633308], zoom_start=12)

    # Listas para armazenar os sentimentos
    sentimentos_roubo = []
    sentimentos_policiamento = []

    # Abra o arquivo TXT para salvar as mensagens
    with open("mensagens_geradas.txt", "w", encoding="utf-8") as arquivo_txt:

        # Itera sobre as linhas do DataFrame
        for index, row in df_roubos.iterrows():
            tipo_crime = "roubo de veículo"
            bairro = row['BAIRRO']
            data_hora = row['DATA_OCORRENCIA_BO']
            hora = row['HORA_OCORRENCIA']
            tipo_carro = row['DESCR_TIPO_VEICULO']

            # Converte 'hora' para datetime dentro do loop (solução mais simples)
            try:
                hora = pd.to_datetime(hora,
                                    format='%H:%M:%S')  # Tenta converter para datetime
                hora_formatada = hora.strftime(
                    '%H:%M:%S')  # Formata se a conversão for bem-sucedida
            except:
                hora_formatada = "Sem informação"  # Define como "Sem informação" se houver erro na conversão

            # Mensagem formatada
            content = f"""Crie um post para as redes sociais alertando sobre um caso real de {tipo_crime} do {tipo_carro}
            ocorrido no bairro de {bairro} 
            no dia {data_hora.strftime('%d/%m/%Y')} às {hora_formatada}h.
            Inclua hashtags relevantes."""

            try:
                completion = client.chat.completions.create(
                    # model="meta-llama/llama-3.2-3b-instruct:free",
                    model="meta-llama/llama-3.2-3b-instruct:free",
                    messages=[{
                        "role": "user",
                        "content": content
                    }])

                try:
                    post_roubo = completion.choices[0].message.content  # Salva o post de roubo
                    print(post_roubo)
                    arquivo_txt.write(
                        f"Post de roubo:\n{post_roubo}\n---\n"
                    )  # Salva o post de roubo no arquivo

                    # Analisa o sentimento do post de roubo
                    sentimento_roubo = sia.polarity_scores(post_roubo)
                    sentimentos_roubo.append(
                        sentimento_roubo)  # Adiciona o sentimento à lista
                    print("Sentimento do post de roubo:", sentimento_roubo)
                    arquivo_txt.write(
                        f"Sentimento do post de roubo: {sentimento_roubo}\n---\n"
                    )  # Salva a análise de sentimento no arquivo

                    # Cria uma nova mensagem com base no sentimento do post de roubo
                    if sentimento_roubo[
                            'compound'] < 0:  # Se o sentimento for negativo
                        content_policiamento = f"""Crie uma mensagem positiva para as redes sociais 
                        elogiando o trabalho de policiamento no bairro {bairro}, 
                        apesar do {tipo_crime} ocorrido. 
                        Mencione que a polícia está trabalhando para garantir a segurança da comunidade."""
                    else:  # Se o sentimento não for negativo
                        content_policiamento = f"""Crie uma mensagem positiva para as redes sociais 
                        sobre o trabalho de policiamento no bairro {bairro}. 
                        Mencione que a polícia está presente e atuante na região, 
                        contribuindo para a segurança da comunidade."""

                    # Gera a mensagem sobre policiamento
                    completion_policiamento = client.chat.completions.create(
                        model="meta-llama/llama-3.2-3b-instruct:free",
                        messages=[{
                            "role": "user",
                            "content": content_policiamento
                        }])

                    try:
                        post_policiamento = completion_policiamento.choices[
                            0].message.content
                        print(post_policiamento)
                        arquivo_txt.write(
                            f"Post de policiamento:\n{post_policiamento}\n---\n"
                        )  # Salva o post de policiamento no arquivo

                        # Analisa o sentimento do post de policiamento
                        sentimento_policiamento = sia.polarity_scores(
                            post_policiamento)
                        sentimentos_policiamento.append(
                            sentimento_policiamento)  # Adiciona o sentimento à lista
                        print("Sentimento do post de policiamento:",
                            sentimento_policiamento)
                        arquivo_txt.write(
                            f"Sentimento do post de policiamento: {sentimento_policiamento}\n---\n"
                        )  # Salva a análise de sentimento no arquivo

                    except TypeError:
                        print(
                            f"Erro: API não retornou conteúdo para policiamento na linha {index}"
                        )
                        print(completion_policiamento)

                except TypeError:
                    print(f"Erro: API não retornou conteúdo na linha {index}")
                    print(completion)

            except Exception as e:
                print(f"Erro ao processar a linha {index}: {e}")
                print(row)

            print("---")

            # Extraia as coordenadas (substitua pelos nomes corretos)
            latitude = row['LATITUDE']
            longitude = row['LONGITUDE']

            # Adicione o marcador ao mapa
            folium.Marker(
                location=[latitude, longitude],
                popup=f"<b>Bairro:</b> {row['BAIRRO']}<br><b>Data:</b> {row['DATA_OCORRENCIA_BO'].strftime('%d/%m/%Y')}<br><b>Hora:</b> {hora_formatada}",
                tooltip="Clique para mais detalhes",
                icon=folium.Icon(color="red", icon="info-sign")).add_to(mapa)

            time.sleep(3)

    # Salve o mapa
    mapa.save("mapa_crimes.html")

    # Gera o gráfico de barras e salva em HTML
    gerar_grafico_sentimentos(sentimentos_roubo, sentimentos_policiamento)


def gerar_grafico_sentimentos(sentimentos_roubo,
                            sentimentos_policiamento):
    # Extrai os scores compostos de cada lista de sentimentos
    scores_roubo = [
        sentimento['compound'] for sentimento in sentimentos_roubo
    ]
    scores_policiamento = [
        sentimento['compound'] for sentimento in sentimentos_policiamento
    ]

    # Cria o gráfico de barras
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(scores_roubo)), scores_roubo, label='Roubo')
    plt.bar(range(len(scores_roubo), len(scores_roubo) + len(scores_policiamento)),
            scores_policiamento,
            label='Policiamento')
    plt.xlabel('Índice da Mensagem')
    plt.ylabel('Score de Sentimento')
    plt.title('Análise de Sentimento dos Posts')
    plt.legend()

    # Salva o gráfico em um arquivo HTML
    tmpfile = BytesIO()
    plt.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
    with open('grafico_sentimentos.html', 'w') as f:
        f.write(html)
    
    # usar apenas se quiser visualizar sem salvar
    # plt.show()


if __name__ == "__main__":  # Executa a função main() quando o script é executado
    main()
