"""
Stratify AI Scoring Engine
Core logic for calculating influence-based probability scores
"""
from typing import Dict, List, Optional
import math
from datetime import datetime, timedelta


class ScoringEngine:
    """
    Calculates asset probability scores based on:
    - Asset sensitivity profile
    - Macro event severity
    - Event sentiment
    - Recency decay
    - Market attention
    
    Formula:
    Influence Score = Asset Sensitivity × Event Severity × Sentiment × Recency × Attention
    """
    
    def __init__(self):
        # Time horizon weights
        self.short_term_weight = 0.6   # 0-4 weeks - recent events matter most
        self.medium_term_weight = 0.3  # 1-6 months - balanced view
        self.long_term_weight = 0.1    # 6-24 months - structural factors
    
    def calculate_recency_score(self, event_date: datetime) -> float:
        """
        Calculate recency decay score
        Recent events have more impact
        
        Args:
            event_date: When the event occurred
            
        Returns:
            Recency score: 1.0 (very recent) to 0.0 (old)
        """
        days_ago = (datetime.utcnow() - event_date).days
        
        # Exponential decay: half-life of 14 days
        half_life = 14
        recency = math.exp(-0.693 * days_ago / half_life)
        
        return max(0.0, min(1.0, recency))
    
    def calculate_influence_score(
        self,
        asset_sensitivity: float,
        event_severity: float,
        event_sentiment: float,
        recency: float,
        attention: float
    ) -> float:
        """
        Calculate single influence score
        
        Args:
            asset_sensitivity: How sensitive asset is to this event type (0-1)
            event_severity: How significant the event is (0-1)
            event_sentiment: Positive or negative (0-1, where 0.5 is neutral)
            recency: How recent the event is (0-1)
            attention: Market attention level (0-1)
            
        Returns:
            Influence score (-1 to +1)
            Positive = upward pressure
            Negative = downward pressure
        """
        # Calculate magnitude of influence
        magnitude = asset_sensitivity * event_severity * recency * attention
        
        # Apply sentiment direction
        # Sentiment below 0.5 is negative, above 0.5 is positive
        direction = (event_sentiment - 0.5) * 2  # Maps 0-1 to -1 to +1
        
        influence = magnitude * direction
        
        return influence
    
    def aggregate_influences(self, influences: List[float]) -> float:
        """
        Aggregate multiple influence scores into single probability
        
        Args:
            influences: List of influence scores
            
        Returns:
            Aggregated probability (0-1)
        """
        if not influences:
            return 0.5  # Neutral if no data
        
        # Sum all influences
        total_influence = sum(influences)
        
        # Convert to probability using sigmoid function
        # This maps (-inf, +inf) to (0, 1)
        probability = 1 / (1 + math.exp(-total_influence))
        
        return probability
    
    def calculate_time_horizon_probabilities(
        self,
        asset_profile: Dict,
        macro_events: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate probabilities for all time horizons
        
        Args:
            asset_profile: Asset sensitivity scores
            macro_events: List of macro events with scores
            
        Returns:
            Dictionary with short, medium, long-term probabilities
        """
        short_term_influences = []
        medium_term_influences = []
        long_term_influences = []
        
        for event in macro_events:
            # Extract event data
            event_type = event.get("event_type", "general")
            severity = event.get("severity_score", 0.5)
            sentiment = event.get("sentiment_score", 0.5)
            attention = event.get("attention_score", 0.5)
            event_date = event.get("created_at", datetime.utcnow())
            
            # Ensure event_date is a datetime object
            if not isinstance(event_date, datetime):
                event_date = datetime.utcnow()
            
            # Calculate recency
            recency = self.calculate_recency_score(event_date)
            
            # Get asset sensitivity for this event type
            sensitivity_key = f"{event_type}_sensitivity"
            asset_sensitivity = asset_profile.get(sensitivity_key, 0.5)
            
            # Calculate influence
            influence = self.calculate_influence_score(
                asset_sensitivity=asset_sensitivity,
                event_severity=severity,
                event_sentiment=sentiment,
                recency=recency,
                attention=attention
            )
            
            # Assign to time horizons based on recency
            days_ago = (datetime.utcnow() - event_date).days
            
            if days_ago <= 30:  # Last month - affects short term
                short_term_influences.append(influence * self.short_term_weight)
            
            if days_ago <= 180:  # Last 6 months - affects medium term
                medium_term_influences.append(influence * self.medium_term_weight)
            
            # All events affect long term
            long_term_influences.append(influence * self.long_term_weight)
        
        # Calculate probabilities
        short_term_prob = self.aggregate_influences(short_term_influences)
        medium_term_prob = self.aggregate_influences(medium_term_influences)
        long_term_prob = self.aggregate_influences(long_term_influences)
        
        return {
            "short_term": round(short_term_prob, 3),
            "medium_term": round(medium_term_prob, 3),
            "long_term": round(long_term_prob, 3)
        }
    
    def determine_confidence_level(
        self,
        num_events: int,
        asset_data_quality: str
    ) -> str:
        """
        Determine confidence level for analysis
        
        Args:
            num_events: Number of macro events analyzed
            asset_data_quality: "high" (from CoinGecko), "medium" (user profile), "low" (minimal data)
            
        Returns:
            Confidence level: "High", "Medium", or "Low"
        """
        # More events and better data = higher confidence
        if asset_data_quality == "high" and num_events >= 5:
            return "High"
        elif asset_data_quality == "medium" or num_events >= 3:
            return "Medium"
        else:
            return "Low"
    
    def create_asset_profile_from_coingecko(self, market_data: Dict) -> Dict:
        """
        Create asset sensitivity profile from CoinGecko market data
        
        Args:
            market_data: Market data from CoinGecko
            
        Returns:
            Asset profile with sensitivity scores
        """
        # Extract or calculate metrics
        volatility = self.calculate_volatility(market_data)
        liquidity = self.calculate_liquidity(market_data)
        
        # Handle market_cap_rank - it might be int, str, or dict
        market_cap_rank = market_data.get("market_cap_rank", 1000)
        if isinstance(market_cap_rank, dict):
            market_cap_rank = 1000
        try:
            market_cap_rank = int(market_cap_rank or 1000)
        except (ValueError, TypeError):
            market_cap_rank = 1000
        
        # Map to sensitivities
        # Higher volatility = more sensitive to events
        # Lower rank (higher market cap) = less sensitive to regulation
        
        profile = {
            "volatility_level": volatility,
            "liquidity_sensitivity": 1.0 - liquidity,  # Lower liquidity = more sensitive
            "regulation_sensitivity": min(market_cap_rank / 100, 1.0),  # Smaller caps more sensitive
            "interest_rate_sensitivity": volatility * 0.8,  # Volatile assets more rate-sensitive
            "geopolitical_sensitivity": volatility * 0.6,
            "data_quality": "high"
        }
        
        return profile
    
    def calculate_volatility(self, market_data: Dict) -> float:
        """Helper to calculate volatility from market data"""
        price_change_24h = market_data.get("price_change_percentage_24h", 0)
        price_change_7d = market_data.get("price_change_percentage_7d", 0)
        
        # Handle if values are dicts (e.g., {"usd": 5.2})
        if isinstance(price_change_24h, dict):
            price_change_24h = price_change_24h.get("usd", 0)
        if isinstance(price_change_7d, dict):
            price_change_7d = price_change_7d.get("usd", 0)
        
        price_change_24h = abs(float(price_change_24h or 0))
        price_change_7d = abs(float(price_change_7d or 0))
        
        avg_volatility = (price_change_24h + price_change_7d) / 2
        return min(avg_volatility / 50, 1.0)
    
    def calculate_liquidity(self, market_data: Dict) -> float:
        """Helper to calculate liquidity from market data"""
        market_cap = market_data.get("market_cap", {})
        volume = market_data.get("total_volume", {})
        
        # Handle if values are dicts (e.g., {"usd": 1000000})
        if isinstance(market_cap, dict):
            market_cap = market_cap.get("usd", 1)
        if isinstance(volume, dict):
            volume = volume.get("usd", 0)
        
        market_cap = float(market_cap or 1)
        volume = float(volume or 0)
        
        volume_ratio = volume / market_cap if market_cap > 0 else 0
        return min(volume_ratio / 0.1, 1.0)


# Create singleton instance
scoring_engine = ScoringEngine()
