import os

from openai import APIError, OpenAI

OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"


class LLMAlertGenerator:
    """Generate alerts through OpenRouter or use local fallback messages."""

    def __init__(self) -> None:
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.client = (
            OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            if api_key
            else None
        )
        if self.client is None:
            print("No OpenRouter API key configured. Using local messages.")

    def generate_message(
        self,
        prompt: str,
        fallback: str,
        row_index: int,
        message_type: str,
    ) -> str:
        if self.client is None:
            return fallback

        try:
            completion = self.client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            message = completion.choices[0].message.content
            if message and message.strip():
                return message.strip()
            raise ValueError("The API returned an empty message.")
        except (APIError, IndexError, ValueError) as error:
            print(
                f"API error generating {message_type} for row {row_index}: {error}. "
                "Using a local message instead."
            )
            return fallback

    def generate_crime_post(
        self,
        tipo_crime: str,
        tipo_carro: str,
        bairro: str,
        data: str,
        hora: str,
        row_index: int = 0,
    ) -> str:
        prompt = (
            f"Crie um post para as redes sociais alertando sobre um caso real de "
            f"{tipo_crime} do {tipo_carro}\nocorrido no bairro de {bairro} no dia "
            f"{data} às {hora}h.\nInclua hashtags relevantes."
        )
        fallback = (
            f"Alerta: foi registrado um {tipo_crime} de {tipo_carro} no bairro "
            f"{bairro}, em {data} às {hora}. Redobre a atenção. #Segurança"
        )
        return self.generate_message(prompt, fallback, row_index, "crime post")

    def generate_policing_post(
        self,
        bairro: str,
        tipo_crime: str,
        is_negative: bool,
        row_index: int = 0,
    ) -> str:
        if is_negative:
            prompt = (
                "Crie uma mensagem positiva para as redes sociais elogiando o trabalho "
                f"de policiamento no bairro {bairro}, apesar do {tipo_crime} ocorrido."
            )
        else:
            prompt = (
                "Crie uma mensagem positiva para as redes sociais sobre o trabalho de "
                f"policiamento no bairro {bairro}."
            )

        fallback = (
            f"Informação para a comunidade do bairro {bairro}: acompanhe os canais "
            "oficiais para atualizações sobre segurança e procure os serviços de "
            "emergência quando necessário. #Segurança #Comunidade"
        )
        return self.generate_message(
            prompt, fallback, row_index, "policing post"
        )
