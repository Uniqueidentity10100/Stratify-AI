"""
Macro data service
Fetches economic indicators from FRED and news from NewsAPI
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.config import settings


class MacroDataService:
    """
    Service for fetching macroeconomic data and news
    Integrates FRED API for economic indicators and NewsAPI for events
    """
    
    def __init__(self):
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        self.fred_api_key = settings.FRED_API_KEY
        self.news_api_key = settings.NEWS_API_KEY
        self.news_base_url = "https://newsapi.org/v2"
    
    def get_interest_rate_data(self) -> Optional[Dict]:
        """
        Fetch current interest rate data from FRED
        
        Returns:
            Dictionary with interest rate information and trend
        """
        try:
            # Federal Funds Rate series
            series_id = "FEDFUNDS"
            url = f"{self.fred_base_url}/series/observations"
            
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 12  # Last 12 months
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get("observations", [])
            
            if not observations:
                return None
            
            # Get current and previous rates
            current_rate = float(observations[0]["value"])
            previous_rate = float(observations[1]["value"]) if len(observations) > 1 else current_rate
            
            # Calculate trend
            trend = "rising" if current_rate > previous_rate else "falling" if current_rate < previous_rate else "stable"
            
            return {
                "current_rate": current_rate,
                "previous_rate": previous_rate,
                "trend": trend,
                "date": observations[0]["date"]
            }
            
        except Exception as e:
            print(f"Error fetching FRED data: {e}")
            return None
    
    def get_inflation_data(self) -> Optional[Dict]:
        """
        Fetch inflation (CPI) data from FRED
        
        Returns:
            Dictionary with inflation information
        """
        try:
            # Consumer Price Index series
            series_id = "CPIAUCSL"
            url = f"{self.fred_base_url}/series/observations"
            
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 12
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get("observations", [])
            
            if len(observations) < 12:
                return None
            
            # Calculate year-over-year inflation
            current_cpi = float(observations[0]["value"])
            year_ago_cpi = float(observations[11]["value"])
            
            yoy_inflation = ((current_cpi - year_ago_cpi) / year_ago_cpi) * 100
            
            return {
                "current_cpi": current_cpi,
                "yoy_inflation": round(yoy_inflation, 2),
                "date": observations[0]["date"]
            }
            
        except Exception as e:
            print(f"Error fetching inflation data: {e}")
            return None
    
    def get_crypto_news(self, query: str = "cryptocurrency regulation") -> List[Dict]:
        """
        Fetch recent cryptocurrency-related news
        
        Args:
            query: Search query for news articles
            
        Returns:
            List of news articles with title, description, and sentiment
        """
        try:
            url = f"{self.news_base_url}/everything"
            
            # Get news from last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "from": from_date,
                "pageSize": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            # Process articles
            processed_articles = []
            for article in articles[:5]:  # Top 5 articles
                processed_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                    "url": article.get("url", "")
                })
            
            return processed_articles
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def get_geopolitical_news(self) -> List[Dict]:
        """
        Fetch geopolitical news that might affect markets
        
        Returns:
            List of geopolitical news articles
        """
        queries = [
            "central bank policy",
            "trade war",
            "financial regulation",
            "economic sanctions"
        ]
        
        all_news = []
        for query in queries:
            news = self.get_crypto_news(query)
            all_news.extend(news)
        
        # Remove duplicates and limit to 10
        unique_news = {article["url"]: article for article in all_news}
        return list(unique_news.values())[:10]
    
    def classify_event_sentiment(self, text: str) -> float:
        """
        Simple sentiment classification for news
        
        Args:
            text: Article title or description
            
        Returns:
            Sentiment score: 0.0 (negative) to 1.0 (positive)
        """
        # Simple keyword-based sentiment (can be enhanced with ML)
        positive_keywords = ["surge", "boom", "adoption", "growth", "positive", "bullish", "rally", "gain"]
        negative_keywords = ["crash", "ban", "regulation", "crackdown", "bearish", "decline", "fall", "risk"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            return 0.7  # Positive sentiment
        elif negative_count > positive_count:
            return 0.3  # Negative sentiment
        else:
            return 0.5  # Neutral


# Create singleton instance
macro_service = MacroDataService()
