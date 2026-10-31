import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict:
        """Retorna as pontuações de polaridade (pos, neg, neu, compound) de um texto."""
        return self.sia.polarity_scores(text)
