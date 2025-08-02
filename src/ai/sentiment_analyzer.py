import requests
from transformers import pipeline
from src.utils.logger import get_logger

logger = get_logger('sentiment_analyzer')

class SentimentAnalyzer:
    def __init__(self):
        try:
            # Try to use GPU if available
            self.nlp = pipeline('sentiment-analysis', device=0)
        except:
            # Fallback to CPU
            self.nlp = pipeline('sentiment-analysis')
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        
    def analyze_text(self, text):
        result = self.nlp(text)[0]
        return {
            'label': result['label'],
            'score': result['score']
        }
        
    def get_token_sentiment(self, token_symbol):
        """Get sentiment from Twitter for a token"""
        if not self.twitter_api_key:
            logger.warning("Twitter API key not set")
            return 0.0
            
        try:
            url = f"https://api.twitter.com/2/tweets/search/recent?query={token_symbol}&max_results=100"
            headers = {"Authorization": f"Bearer {self.twitter_api_key}"}
            response = requests.get(url, headers=headers)
            tweets = response.json().get('data', [])
            
            positive_count = 0
            total_count = len(tweets)
            
            for tweet in tweets:
                result = self.analyze_text(tweet['text'])
                if result['label'] == 'POSITIVE':
                    positive_count += 1
                    
            return positive_count / total_count if total_count > 0 else 0.5
        except Exception as e:
            logger.error(f"Twitter sentiment failed: {e}")
            return 0.5
