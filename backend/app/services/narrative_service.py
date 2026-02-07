"""
AI Narrative Service
Uses a local LLM via Ollama to convert structured scores into plain English explanations
Ollama provides an OpenAI-compatible API, so the interface is identical.
"""
from openai import OpenAI
from typing import Dict, List
from app.config import settings


class NarrativeService:
    """
    Converts structured probability scores into human-readable narratives
    Uses Ollama (local open-source LLM) for natural language generation
    
    IMPORTANT: This service only explains pre-calculated scores
    It does NOT calculate probabilities itself
    
    Setup: Install Ollama (https://ollama.com) and pull a model:
        ollama pull llama3.1:8b
    """
    
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama"  # Ollama doesn't require a real key
        )
        self.model = settings.OLLAMA_MODEL
    
    def generate_time_horizon_narrative(
        self,
        asset_name: str,
        time_horizon: str,
        probability: float,
        macro_events: List[Dict],
        asset_profile: Dict
    ) -> str:
        """
        Generate narrative explanation for a specific time horizon
        
        Args:
            asset_name: Name of the asset
            time_horizon: "short", "medium", or "long"
            probability: Pre-calculated probability score
            macro_events: List of relevant macro events
            asset_profile: Asset sensitivity profile
            
        Returns:
            Plain English explanation
        """
        # Build context for GPT
        events_summary = self._summarize_events(macro_events)
        sensitivity_summary = self._summarize_sensitivities(asset_profile)
        
        # Interpret probability
        outlook = self._interpret_probability(probability)
        
        prompt = f"""You are a financial analyst explaining macro influence analysis to a beginner.

Asset: {asset_name}
Time Horizon: {time_horizon}-term ({"0-4 weeks" if time_horizon == "short" else "1-6 months" if time_horizon == "medium" else "6-24 months"})
Calculated Probability Score: {probability:.2f} (on scale 0-1, where 0.5 is neutral)
Outlook: {outlook}

Asset Sensitivity Profile:
{sensitivity_summary}

Recent Macro Events:
{events_summary}

Task: Write a 2-3 sentence explanation in plain English that:
1. Explains what the {probability:.2f} score means for {asset_name}
2. References the most relevant macro events
3. Uses simple language, no jargon
4. Sounds like a teacher explaining to a student

Do not recalculate anything. Just explain the provided score."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a patient financial educator who explains complex topics simply."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            narrative = response.choices[0].message.content.strip()
            return narrative
            
        except Exception as e:
            print(f"Error generating narrative: {e}")
            return f"The {time_horizon}-term outlook shows a probability of {probability:.2f}, suggesting {outlook} conditions."
    
    def generate_most_likely_scenario(
        self,
        asset_name: str,
        probabilities: Dict[str, float],
        macro_events: List[Dict]
    ) -> str:
        """
        Generate the most likely scenario based on all probabilities
        
        Args:
            asset_name: Name of the asset
            probabilities: Dict with short, medium, long-term probabilities
            macro_events: List of macro events
            
        Returns:
            Scenario description
        """
        events_summary = self._summarize_events(macro_events[:5])  # Top 5 events
        
        prompt = f"""Based on this macro analysis for {asset_name}:

Short-term probability: {probabilities['short_term']:.2f}
Medium-term probability: {probabilities['medium_term']:.2f}
Long-term probability: {probabilities['long_term']:.2f}

Key macro events:
{events_summary}

Write a single paragraph (3-4 sentences) describing the most likely scenario for this asset over the next 6 months. Use simple language and be specific about what might happen."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst writing scenario analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating scenario: {e}")
            return "Based on current macro conditions, the asset faces mixed pressures across different time horizons."
    
    def _summarize_events(self, events: List[Dict]) -> str:
        """Create bullet point summary of events"""
        if not events:
            return "- No significant macro events in recent period"
        
        summary_lines = []
        for event in events[:5]:  # Top 5
            event_type = event.get("event_type", "general").replace("_", " ").title()
            description = event.get("event_description", "No description")[:100]
            summary_lines.append(f"- {event_type}: {description}")
        
        return "\n".join(summary_lines)
    
    def _summarize_sensitivities(self, profile: Dict) -> str:
        """Create summary of asset sensitivities"""
        sensitivities = []
        
        for key, value in profile.items():
            if "_sensitivity" in key and isinstance(value, (int, float)):
                factor = key.replace("_sensitivity", "").replace("_", " ").title()
                level = "High" if value > 0.7 else "Medium" if value > 0.4 else "Low"
                sensitivities.append(f"- {factor}: {level} ({value:.2f})")
        
        return "\n".join(sensitivities) if sensitivities else "- Balanced sensitivity profile"
    
    def _interpret_probability(self, probability: float) -> str:
        """Convert probability to qualitative description"""
        if probability > 0.7:
            return "strongly positive"
        elif probability > 0.6:
            return "moderately positive"
        elif probability > 0.4:
            return "neutral to slightly positive"
        elif probability > 0.3:
            return "neutral to slightly negative"
        else:
            return "negative"


# Create singleton instance
narrative_service = NarrativeService()
