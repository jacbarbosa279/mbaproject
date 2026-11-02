import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon", quiet=True)


class SentimentAnalyzer:
    def __init__(self) -> None:
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict[str, float]:
        """Return VADER polarity scores, including the compound score."""
        return self.sia.polarity_scores(text)
