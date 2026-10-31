import os
from openai import OpenAI

class LLMAlertGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENAI_API_KEY")
        )

    def generate_crime_post(self, tipo_crime: str, tipo_carro: str, bairro: str, data: str, hora: str) -> str:
        content = f"""Crie um post para as redes sociais alertando sobre um caso real de {tipo_crime} do {tipo_carro}
        ocorrido no bairro de {bairro} no dia {data} às {hora}h. Inclua hashtags relevantes."""
        
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[{"role": "user", "content": content}]
        )
        return completion.choices[0].message.content

    def generate_policing_post(self, bairro: str, tipo_crime: str, is_negative: bool) -> str:
        if is_negative:
            content = f"Crie uma mensagem positiva para as redes sociais elogiando o trabalho de policiamento no bairro {bairro}, apesar do {tipo_crime} ocorrido."
        else:
            content = f"Crie uma mensagem positiva para as redes sociais sobre o trabalho de policiamento no bairro {bairro}."

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[{"role": "user", "content": content}]
        )
        return completion.choices[0].message.content
