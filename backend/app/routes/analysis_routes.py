"""
Analysis routes
Main routes for asset analysis and report generation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
import os

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.models.macro_event import MacroEvent
from app.schemas.asset_schema import AssetQuery, TokenProfileCreate, AnalysisResponse
from app.utils.jwt_handler import get_current_user
from app.services.coingecko_service import coingecko_service
from app.services.macro_service import macro_service
from app.services.scoring_engine import scoring_engine
from app.services.narrative_service import narrative_service
from app.services.pdf_service import pdf_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/analyze", response_model=Dict)
def analyze_asset(
    query: AssetQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze an asset and generate probability scores
    
    This is the main endpoint that orchestrates:
    1. Asset discovery (CoinGecko or user profile)
    2. Macro data collection (FRED + NewsAPI)
    3. Scoring engine calculation
    4. AI narrative generation
    5. Report storage
    
    Returns complete analysis with probabilities and narratives
    """
    asset_name = query.asset_name
    
    # Step 1: Try to find asset in CoinGecko
    print(f"Searching for asset: {asset_name}")
    coin_data = coingecko_service.search_asset(asset_name)
    
    asset_profile = None
    asset_found = False
    coin_image = ""
    coin_description = ""
    display_market_data = {}
    
    if coin_data:
        # Asset found in CoinGecko - get detailed data
        coin_id = coin_data.get("id")
        details = coingecko_service.get_asset_details(coin_id)
        
        if details and details.get("market_data"):
            asset_found = True
            market_data = details["market_data"]
            
            # Create asset profile from market data
            asset_profile = scoring_engine.create_asset_profile_from_coingecko(market_data)
            asset_profile["asset_name"] = details.get("name", asset_name)
            asset_profile["symbol"] = details.get("symbol", "").upper()
            
            # Extract enriched data for frontend display
            coin_image = details.get("image", {}).get("large", "")
            coin_description = (details.get("description", {}).get("en", "") or "")[:500]
            
            def _safe_usd(val):
                if isinstance(val, dict):
                    return val.get("usd", 0)
                return val if val is not None else 0
            
            display_market_data = {
                "current_price": _safe_usd(market_data.get("current_price")),
                "market_cap": _safe_usd(market_data.get("market_cap")),
                "total_volume": _safe_usd(market_data.get("total_volume")),
                "price_change_24h": market_data.get("price_change_percentage_24h", 0) or 0,
                "price_change_7d": market_data.get("price_change_percentage_7d", 0) or 0,
                "price_change_30d": market_data.get("price_change_percentage_30d", 0) or 0,
                "market_cap_rank": market_data.get("market_cap_rank"),
                "ath": _safe_usd(market_data.get("ath")),
                "ath_change_percentage": _safe_usd(market_data.get("ath_change_percentage")),
                "high_24h": _safe_usd(market_data.get("high_24h")),
                "low_24h": _safe_usd(market_data.get("low_24h")),
                "circulating_supply": market_data.get("circulating_supply", 0) or 0,
                "total_supply": market_data.get("total_supply", 0) or 0,
            }
    
    if not asset_found:
        # Asset not found - return message to create custom profile
        return {
            "asset_found": False,
            "message": "Asset not found in CoinGecko. Please create a custom profile.",
            "requires_profile": True
        }
    
    # Step 2: Fetch macro data
    print("Fetching macro data...")
    
    # Get economic indicators
    interest_rate_data = macro_service.get_interest_rate_data()
    inflation_data = macro_service.get_inflation_data()
    
    # Get news
    crypto_news = macro_service.get_crypto_news(f"{asset_name} cryptocurrency")
    general_news = macro_service.get_geopolitical_news()
    
    # Step 3: Create macro events for scoring
    macro_events = []
    
    # Interest rate event
    if interest_rate_data:
        macro_events.append({
            "event_type": "interest_rate",
            "event_description": f"Federal funds rate at {interest_rate_data['current_rate']}%, trend {interest_rate_data['trend']}",
            "severity_score": 0.7,
            "sentiment_score": 0.4 if interest_rate_data['trend'] == 'rising' else 0.6,
            "attention_score": 0.8,
            "created_at": datetime.utcnow()
        })
    
    # Inflation event
    if inflation_data:
        macro_events.append({
            "event_type": "interest_rate",
            "event_description": f"Inflation at {inflation_data['yoy_inflation']}% year-over-year",
            "severity_score": min(abs(inflation_data['yoy_inflation']) / 10, 1.0),
            "sentiment_score": 0.3 if inflation_data['yoy_inflation'] > 3 else 0.6,
            "attention_score": 0.7,
            "created_at": datetime.utcnow()
        })
    
    # News events
    news_with_sentiment = []
    for article in crypto_news[:5]:
        sentiment = macro_service.classify_event_sentiment(
            article['title'] + " " + article.get('description', '')
        )
        
        news_with_sentiment.append({
            "title": article.get("title", ""),
            "source": article.get("source", "Unknown"),
            "url": article.get("url", ""),
            "published_at": article.get("published_at", ""),
            "sentiment": round(sentiment, 2)
        })
        
        macro_events.append({
            "event_type": "regulation",
            "event_description": article['title'],
            "severity_score": 0.6,
            "sentiment_score": sentiment,
            "attention_score": 0.7,
            "created_at": datetime.utcnow()
        })
    
    # Step 4: Calculate probabilities using scoring engine
    print("Calculating probabilities...")
    probabilities = scoring_engine.calculate_time_horizon_probabilities(
        asset_profile=asset_profile,
        macro_events=macro_events
    )
    
    # Step 5: Generate AI narratives
    print("Generating narratives...")
    narratives = {}
    
    for horizon in ['short', 'medium', 'long']:
        prob_key = f"{horizon}_term"
        narratives[horizon] = narrative_service.generate_time_horizon_narrative(
            asset_name=asset_profile['asset_name'],
            time_horizon=horizon,
            probability=probabilities[prob_key],
            macro_events=macro_events,
            asset_profile=asset_profile
        )
    
    # Generate most likely scenario
    most_likely = narrative_service.generate_most_likely_scenario(
        asset_name=asset_profile['asset_name'],
        probabilities=probabilities,
        macro_events=macro_events
    )
    
    # Determine confidence
    confidence = scoring_engine.determine_confidence_level(
        num_events=len(macro_events),
        asset_data_quality=asset_profile.get('data_quality', 'medium')
    )
    
    # Build factor breakdown for frontend
    factor_breakdown = {
        "volatility": round(asset_profile.get("volatility_level", 0.5), 2),
        "liquidity": round(1.0 - asset_profile.get("liquidity_sensitivity", 0.5), 2),
        "regulation_exposure": round(asset_profile.get("regulation_sensitivity", 0.5), 2),
        "interest_rate_impact": round(asset_profile.get("interest_rate_sensitivity", 0.5), 2),
        "geopolitical_risk": round(asset_profile.get("geopolitical_sensitivity", 0.5), 2),
    }
    
    # Collect macro data for frontend
    macro_display = {
        "interest_rate": interest_rate_data,
        "inflation": inflation_data
    }
    
    # Step 6: Save report to database
    report = Report(
        user_id=current_user.id,
        token_name=asset_profile['asset_name'],
        short_term_prob=probabilities['short_term'],
        medium_term_prob=probabilities['medium_term'],
        long_term_prob=probabilities['long_term'],
        short_term_narrative=narratives['short'],
        medium_term_narrative=narratives['medium'],
        long_term_narrative=narratives['long'],
        most_likely_scenario=most_likely,
        confidence_level=confidence
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Return complete analysis
    return {
        "asset_found": True,
        "asset_name": asset_profile['asset_name'],
        "symbol": asset_profile.get('symbol', ''),
        "image": coin_image,
        "description": coin_description,
        "market_data": display_market_data,
        "probabilities": probabilities,
        "narratives": narratives,
        "most_likely_scenario": most_likely,
        "confidence_level": confidence,
        "report_id": str(report.id),
        "macro_events_analyzed": len(macro_events),
        "news_sources": news_with_sentiment,
        "macro_data": macro_display,
        "factor_breakdown": factor_breakdown
    }


@router.get("/reports", response_model=Dict)
def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for current user
    """
    reports = db.query(Report).filter(Report.user_id == current_user.id)\
        .order_by(Report.created_at.desc()).limit(20).all()
    
    reports_data = []
    for report in reports:
        reports_data.append({
            "id": str(report.id),
            "token_name": report.token_name,
            "short_term_prob": report.short_term_prob,
            "medium_term_prob": report.medium_term_prob,
            "long_term_prob": report.long_term_prob,
            "confidence_level": report.confidence_level,
            "created_at": report.created_at.isoformat()
        })
    
    return {
        "reports": reports_data,
        "total": len(reports_data)
    }


@router.post("/generate-pdf/{report_id}")
def generate_pdf_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate PDF for a specific report
    """
    # Find report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Generate PDF
    probabilities = {
        "short_term": report.short_term_prob,
        "medium_term": report.medium_term_prob,
        "long_term": report.long_term_prob
    }
    
    narratives = {
        "short_term": report.short_term_narrative,
        "medium_term": report.medium_term_narrative,
        "long_term": report.long_term_narrative
    }
    
    # Create macro summary
    macro_summary = "Current macro conditions analyzed include interest rates, inflation, and regulatory developments affecting the crypto market."
    
    pdf_path = pdf_service.generate_report(
        asset_name=report.token_name,
        probabilities=probabilities,
        narratives=narratives,
        most_likely_scenario=report.most_likely_scenario,
        confidence_level=report.confidence_level,
        macro_summary=macro_summary,
        user_email=current_user.email
    )
    
    # Update report with PDF path
    report.pdf_path = pdf_path
    db.commit()
    
    return FileResponse(
        path=pdf_path,
        media_type='application/pdf',
        filename=os.path.basename(pdf_path),
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(pdf_path)}"}
    )
