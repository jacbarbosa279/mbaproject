FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    NLTK_DATA=/usr/local/share/nltk_data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader -d "$NLTK_DATA" vader_lexicon

COPY main_script_app_sentimento.py .
COPY data/raw/ ./data/raw/

RUN mkdir -p output data/processed

VOLUME ["/app/output", "/app/data/processed"]

CMD ["python", "main_script_app_sentimento.py"]
