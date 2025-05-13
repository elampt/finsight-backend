import yfinance as yf
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load FinBERT model and tokenizer
finbert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
finbert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")

# Initialize the sentiment analysis pipeline
finbert_pipeline = pipeline("sentiment-analysis", model=finbert_model, tokenizer=finbert_tokenizer)

def fetch_news(stock_symbol: str, news_count: int = 5):
    """
    Fetch news articles related to a stock symbol using yfinance.
    """
    search = yf.Search(stock_symbol, news_count=news_count)
    return search.news

def analyze_sentiment(news_articles):
    """
    Analyze the sentiment of a list of news articles using FinBERT.
    """
    analyzed_articles = []
    sentiment_summary = {"positive": 0, "negative": 0, "neutral": 0}

    for article in news_articles:
        title = article['title']
        sentiment = finbert_pipeline(title)[0]
        sentiment_label = sentiment['label'].lower()
        sentiment_summary[sentiment_label] += 1

        analyzed_articles.append({
            "title": title,
            "publisher": article.get('publisher', 'Unknown'),
            "link": article.get('link', '#'),
            "sentiment": sentiment_label,
            "confidence": round(sentiment['score'], 4)
        })

    return analyzed_articles, sentiment_summary