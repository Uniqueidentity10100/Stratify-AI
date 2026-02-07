"""
Asset and analysis schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict


class AssetQuery(BaseModel):
    """
    Schema for asset analysis request
    """
    asset_name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_name": "Bitcoin"
            }
        }


class TokenProfileCreate(BaseModel):
    """
    Schema for creating custom token profile
    Used when asset is not found in CoinGecko
    """
    token_name: str
    token_type: str
    volatility_level: float
    liquidity_sensitivity: float
    regulation_sensitivity: float
    interest_rate_sensitivity: float
    geopolitical_sensitivity: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "token_name": "CustomToken",
                "token_type": "DeFi",
                "volatility_level": 0.8,
                "liquidity_sensitivity": 0.7,
                "regulation_sensitivity": 0.9,
                "interest_rate_sensitivity": 0.6,
                "geopolitical_sensitivity": 0.5
            }
        }


class AnalysisResponse(BaseModel):
    """
    Schema for analysis results
    """
    asset_name: str
    asset_found: bool
    short_term_probability: float
    medium_term_probability: float
    long_term_probability: float
    confidence_level: str
    analysis_summary: Optional[str] = None
