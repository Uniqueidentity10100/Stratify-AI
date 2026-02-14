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
    - Market momentum (actual price direction)
    - Asset sensitivity profile
    - Macro event severity & sentiment
    - Recency decay
    - Market attention
    
    Influence Score = Amplification × Σ(Sensitivity × Severity × Sentiment × Recency × Attention)
    Final Score = sigmoid(Market Momentum + Macro Influence)
    """
    
    def __init__(self):
        # Amplification factor to make influences meaningful in sigmoid
        self.amplification = 8.0
        
        # Market momentum weights per horizon
        self.momentum_weights = {
            "short_term": {"24h": 0.5, "7d": 0.3, "30d": 0.2},
            "medium_term": {"24h": 0.15, "7d": 0.35, "30d": 0.50},
            "long_term": {"24h": 0.05, "7d": 0.15, "30d": 0.80},
        }
        
        # Minimum sensitivity floor so no factor is ever zero
        self.min_sensitivity = 0.15
    
    def calculate_recency_score(self, event_date: datetime) -> float:
        """
        Calculate recency decay score
        Recent events have more impact
        """
        days_ago = (datetime.utcnow() - event_date).days
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
        
        Returns:
            Influence score (-1 to +1)
        """
        # Ensure sensitivity has a floor
        asset_sensitivity = max(asset_sensitivity, self.min_sensitivity)
        
        magnitude = asset_sensitivity * event_severity * recency * attention
        direction = (event_sentiment - 0.5) * 2  # Maps 0-1 to -1 to +1
        
        return magnitude * direction
    
    def calculate_momentum_signal(
        self,
        price_changes: Dict[str, float],
        horizon: str
    ) -> float:
        """
        Calculate market momentum signal from actual price changes.
        This gives the scoring engine real market direction data.
        
        Args:
            price_changes: Dict with '24h', '7d', '30d' percentage changes
            horizon: 'short_term', 'medium_term', or 'long_term'
            
        Returns:
            Momentum score (-1 to +1) representing market direction
        """
        weights = self.momentum_weights.get(horizon, {"24h": 0.33, "7d": 0.33, "30d": 0.34})
        
        # Normalize price changes: ±10% maps to ±1.0
        def normalize(pct):
            return max(-1.0, min(1.0, pct / 10.0))
        
        momentum = (
            weights["24h"] * normalize(price_changes.get("24h", 0)) +
            weights["7d"] * normalize(price_changes.get("7d", 0)) +
            weights["30d"] * normalize(price_changes.get("30d", 0))
        )
        
        return momentum
    
    def aggregate_influences(
        self,
        influences: List[float],
        momentum: float = 0.0
    ) -> float:
        """
        Aggregate multiple influence scores into single probability
        
        Args:
            influences: List of influence scores
            momentum: Market momentum signal (-1 to +1)
            
        Returns:
            Aggregated probability (0-1)
        """
        if not influences and momentum == 0.0:
            return 0.5  # Neutral if no data
        
        # Sum macro influences and amplify
        macro_signal = sum(influences) * self.amplification
        
        # Combine momentum (weighted 60%) with macro analysis (weighted 40%)
        # Momentum is direct market evidence, macro is forward-looking
        combined = momentum * 2.5 + macro_signal
        
        # Sigmoid to probability
        probability = 1 / (1 + math.exp(-combined))
        
        return probability
    
    def calculate_time_horizon_probabilities(
        self,
        asset_profile: Dict,
        macro_events: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate probabilities for all time horizons
        
        Uses both market momentum (actual price direction) and
        macro event analysis (forward-looking sentiment) for each horizon.
        """
        # Extract price changes for momentum calculation
        price_changes = {
            "24h": asset_profile.get("price_change_24h", 0),
            "7d": asset_profile.get("price_change_7d", 0),
            "30d": asset_profile.get("price_change_30d", 0),
        }
        
        short_term_influences = []
        medium_term_influences = []
        long_term_influences = []
        
        for event in macro_events:
            event_type = event.get("event_type", "general")
            severity = event.get("severity_score", 0.5)
            sentiment = event.get("sentiment_score", 0.5)
            attention = event.get("attention_score", 0.5)
            event_date = event.get("created_at", datetime.utcnow())
            
            if not isinstance(event_date, datetime):
                event_date = datetime.utcnow()
            
            recency = self.calculate_recency_score(event_date)
            
            sensitivity_key = f"{event_type}_sensitivity"
            asset_sensitivity = asset_profile.get(sensitivity_key, 0.4)
            
            influence = self.calculate_influence_score(
                asset_sensitivity=asset_sensitivity,
                event_severity=severity,
                event_sentiment=sentiment,
                recency=recency,
                attention=attention
            )
            
            days_ago = (datetime.utcnow() - event_date).days
            
            if days_ago <= 30:
                short_term_influences.append(influence)
            if days_ago <= 180:
                medium_term_influences.append(influence)
            long_term_influences.append(influence)
        
        # Calculate momentum for each horizon
        short_momentum = self.calculate_momentum_signal(price_changes, "short_term")
        medium_momentum = self.calculate_momentum_signal(price_changes, "medium_term")
        long_momentum = self.calculate_momentum_signal(price_changes, "long_term")
        
        # Calculate final probabilities with momentum + macro
        short_term_prob = self.aggregate_influences(short_term_influences, short_momentum)
        medium_term_prob = self.aggregate_influences(medium_term_influences, medium_momentum)
        long_term_prob = self.aggregate_influences(long_term_influences, long_momentum)
        
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
        """
        if asset_data_quality == "high" and num_events >= 5:
            return "High"
        elif asset_data_quality == "medium" or num_events >= 3:
            return "Medium"
        else:
            return "Low"
    
    def create_asset_profile_from_coingecko(self, market_data: Dict) -> Dict:
        """
        Create asset sensitivity profile from CoinGecko market data.
        Also stores raw price change data for momentum calculation.
        """
        volatility = self.calculate_volatility(market_data)
        liquidity = self.calculate_liquidity(market_data)
        
        # Handle market_cap_rank
        market_cap_rank = market_data.get("market_cap_rank", 1000)
        if isinstance(market_cap_rank, dict):
            market_cap_rank = 1000
        try:
            market_cap_rank = int(market_cap_rank or 1000)
        except (ValueError, TypeError):
            market_cap_rank = 1000
        
        # Extract price changes (handle dict values)
        def _safe_float(val, key="usd"):
            if isinstance(val, dict):
                return float(val.get(key, 0) or 0)
            return float(val or 0)
        
        price_change_24h = _safe_float(market_data.get("price_change_percentage_24h", 0))
        price_change_7d = _safe_float(market_data.get("price_change_percentage_7d", 0))
        price_change_30d = _safe_float(market_data.get("price_change_percentage_30d", 0))
        
        # Sensitivity floors: even stablecoins have some macro sensitivity
        profile = {
            "volatility_level": max(volatility, 0.05),
            "liquidity_sensitivity": max(1.0 - liquidity, self.min_sensitivity),
            "regulation_sensitivity": max(min(market_cap_rank / 100, 1.0), self.min_sensitivity),
            "interest_rate_sensitivity": max(volatility * 0.8 + 0.15, self.min_sensitivity),
            "geopolitical_sensitivity": max(volatility * 0.6 + 0.1, self.min_sensitivity),
            "data_quality": "high",
            # Raw price changes for momentum engine
            "price_change_24h": price_change_24h,
            "price_change_7d": price_change_7d,
            "price_change_30d": price_change_30d,
        }
        
        return profile
    
    def calculate_volatility(self, market_data: Dict) -> float:
        """Helper to calculate volatility from market data"""
        price_change_24h = market_data.get("price_change_percentage_24h", 0)
        price_change_7d = market_data.get("price_change_percentage_7d", 0)
        
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
