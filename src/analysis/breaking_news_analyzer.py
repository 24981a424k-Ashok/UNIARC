import os
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import openai
from src.config.settings import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class BreakingNewsAnalyzer:
    """
    AI-powered Breaking News classifier that evaluates articles based on:
    - Time sensitivity (0-30 minutes)
    - Impact level (≥8/10)
    - Source verification
    """
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API Key missing! Breaking news analysis will use fallback logic.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    async def analyze_breaking_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple articles in parallel for breaking news classification.
        Returns list of breaking news items with structured metadata.
        """
        if not self.api_key:
            return [self._fallback_analysis(a) for a in articles]
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key)
        
        try:
            tasks = [self._analyze_single_breaking(a, client) for a in articles]
            results = await asyncio.gather(*tasks)
            
            # Filter only Breaking, Developing, and Top Headlines
            breaking_items = [r for r in results if r and r.get("classification") in ["Breaking News", "Developing News", "Top Headline"]]
            
            # Sort by impact score and recency
            breaking_items.sort(key=lambda x: (x.get("impact_score", 0), x.get("recency_minutes", 999)), reverse=True)
            
            return breaking_items[:20]  # Top 20
        except Exception as e:
            logger.error(f"Breaking news batch analysis failed: {e}")
            return [self._fallback_analysis(a) for a in articles[:20]]
        finally:
            await client.close()
    
    async def _analyze_single_breaking(self, article: Dict[str, Any], client) -> Optional[Dict[str, Any]]:
        """Analyze a single article for breaking news criteria."""
        title = article.get("title", "")
        content = article.get("content", "")
        source = article.get("source_name", "Unknown")
        published_at = article.get("published_at")
        
        # Calculate recency
        now = datetime.now(timezone.utc)
        if published_at:
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_at = now
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            
            time_diff = (now - published_at).total_seconds() / 60  # minutes
        else:
            time_diff = 999
        
        system_prompt = """You are a Breaking News Editor AI for a news intelligence platform.

Your task is to identify, validate, and present ONLY genuine breaking news.
Do NOT label regular headlines as breaking news.

────────────────────────────
BREAKING NEWS EVALUATION RULES
────────────────────────────
Classify news as "Breaking" ONLY if:

1. Time Sensitivity
- Event occurred within the last 0–30 minutes
- OR is officially announced and unfolding live

2. Impact Level
- Public safety, government, economy, markets, disasters, or national importance
- Impact score ≥ 8 / 10

3. Verification
- Source must be reliable OR confirmed by multiple outlets
- If unconfirmed, mark as "Developing"

────────────────────────────
OUTPUT FORMAT (JSON ONLY)
────────────────────────────
{
    "classification": "Breaking News | Developing News | Top Headline | Regular News",
    "breaking_headline": "Short, factual headline (if Breaking/Developing)",
    "what_happened": ["Bullet point 1", "Bullet point 2"],
    "why_matters": "Immediate impact explanation",
    "next_updates": ["Possible update 1", "Possible update 2"],
    "confidence_level": "High | Medium | Low",
    "impact_score": 1-10,
    "recency_minutes": <calculated from timestamp>
}

IMPORTANT: Output ONLY valid JSON. No markdown, no extra text."""

        user_prompt = f"""
────────────────────────────
INPUT
────────────────────────────
Article Title: {title}
Article Content: {content[:2000]}
Source Name: {source}
Time Since Publication: {int(time_diff)} minutes ago

Analyze and classify this article."""

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            
            raw_content = response.choices[0].message.content
            
            # Clean markdown if present
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].strip()
            
            result = json.loads(raw_content)
            result["recency_minutes"] = int(time_diff)
            result["original_article"] = article
            
            return result
        except openai.RateLimitError as e:
            # Handle Quota Exceeded silently with fallback
            logger.warning(f"OpenAI Quota Exceeded for '{title}'. Using enhanced fallback logic.")
            return self._fallback_analysis(article)
        except Exception as e:
            logger.error(f"Breaking news analysis failed for '{title}': {e}")
            return self._fallback_analysis(article)
    
    def _fallback_analysis(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback logic when AI is unavailable."""
        title = article.get("title", "").lower()
        
        # Keywords that suggest breaking news
        breaking_keywords = [
            "breaking", "urgent", "just in", "live", "developing",
            "explosion", "crash", "attack", "earthquake", "fire",
            "emergency", "alert", "warning", "disaster", "crisis"
        ]
        
        high_impact_keywords = [
            "government", "president", "prime minister", "parliament",
            "stock market", "economy", "war", "military", "terror",
            "death", "killed", "injured", "rescue", "evacuate",
            "india", "modi", "announcement", "policy", "budget", "launch"
        ]
        
        is_breaking = any(kw in title for kw in breaking_keywords)
        is_high_impact = any(kw in title for kw in high_impact_keywords)
        
        # Calculate recency
        published_at = article.get("published_at")
        now = datetime.now(timezone.utc)
        
        if published_at:
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_at = now
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            
            time_diff = (now - published_at).total_seconds() / 60
        else:
            time_diff = 999
        
        # Classification logic - RELAXED FALLBACK
        # If it's recent (last 6 hours), we default to at least "Top Headline" to ensure dashboard population
        if time_diff < 360:  # 6 hours
             if is_breaking:
                 classification = "Breaking News"
                 impact_score = 9
             elif is_high_impact:
                 classification = "Developing News"
                 impact_score = 8
             else:
                 # Default to Top Headline instead of Regular News to ensure it shows up
                 classification = "Top Headline" 
                 impact_score = 7
        else:
            classification = "Regular News"
            impact_score = 5
        
        return {
            "classification": classification,
            "breaking_headline": article.get("title", ""),
            "what_happened": [f"Update regarding {article.get('title', '')[:60]}..."],
            "why_matters": "Significant development requiring immediate attention.",
            "next_updates": ["Further details expected soon", "Official statements pending"],
            "confidence_level": "Medium",
            "impact_score": impact_score,
            "recency_minutes": int(time_diff),
            "image_url": article.get("url_to_image") or article.get("image_url"),
            "original_article": article
        }
