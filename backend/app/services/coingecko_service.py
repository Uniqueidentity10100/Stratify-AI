"""
CoinGecko API service
Fetches cryptocurrency data and market information
"""
import requests
from typing import Optional, Dict
from app.config import settings


class CoinGeckoService:
    """
    Service for interacting with CoinGecko API
    Provides asset lookup and market data
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {}
        
        # Add API key if available (for Pro tier)
        if settings.COINGECKO_API_KEY:
            self.headers["x-cg-pro-api-key"] = settings.COINGECKO_API_KEY
    
    def search_asset(self, asset_name: str) -> Optional[Dict]:
        """
        Search for a cryptocurrency by name or symbol
        
        Args:
            asset_name: Name or symbol of the asset (e.g., "Bitcoin" or "BTC")
            
        Returns:
            Dictionary with asset data if found, None otherwise
            
        Example response:
            {
                "id": "bitcoin",
                "name": "Bitcoin",
                "symbol": "BTC",
                "market_cap_rank": 1
            }
        """
        try:
            # Search endpoint
            url = f"{self.base_url}/search"
            params = {"query": asset_name}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Return first coin result if found
            if data.get("coins") and len(data["coins"]) > 0:
                return data["coins"][0]
            
            return None
            
        except Exception as e:
            print(f"Error searching CoinGecko: {e}")
            return None
    
    def get_asset_details(self, coin_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific cryptocurrency
        
        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin")
            
        Returns:
            Detailed asset information including market data
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching asset details: {e}")
            return None
    
    def calculate_volatility_score(self, market_data: Dict) -> float:
        """
        Calculate asset volatility score from market data
        
        Args:
            market_data: Market data from CoinGecko API
            
        Returns:
            Volatility score between 0.0 and 1.0
        """
        try:
            # Get price change percentages
            price_change_24h = abs(market_data.get("price_change_percentage_24h", 0))
            price_change_7d = abs(market_data.get("price_change_percentage_7d", 0))
            price_change_30d = abs(market_data.get("price_change_percentage_30d", 0))
            
            # Calculate average volatility
            # Higher percentage changes = higher volatility
            avg_volatility = (price_change_24h + price_change_7d + price_change_30d) / 3
            
            # Normalize to 0-1 scale (cap at 50% for normalization)
            volatility_score = min(avg_volatility / 50, 1.0)
            
            return volatility_score
            
        except Exception:
            return 0.5  # Default medium volatility
    
    def calculate_liquidity_score(self, market_data: Dict) -> float:
        """
        Calculate liquidity score based on market cap and volume
        
        Args:
            market_data: Market data from CoinGecko API
            
        Returns:
            Liquidity score between 0.0 and 1.0
        """
        try:
            market_cap = market_data.get("market_cap", 0)
            total_volume = market_data.get("total_volume", 0)
            
            # Calculate volume to market cap ratio
            if market_cap > 0:
                volume_ratio = total_volume / market_cap
                # Higher ratio = higher liquidity
                # Normalize: 0.1 ratio = high liquidity
                liquidity_score = min(volume_ratio / 0.1, 1.0)
            else:
                liquidity_score = 0.1
            
            return liquidity_score
            
        except Exception:
            return 0.5  # Default medium liquidity


# Create singleton instance
coingecko_service = CoinGeckoService()
