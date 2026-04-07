import os
import requests
import json
import logging
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class CricketService:
    """
    Live Cricket Score Service using CricketData.org (CricAPI).
    Fetches real-time scores for matches involving "India" or "IPL".
    """
    
    def __init__(self):
        self.api_key = os.getenv("CRICKET_API_KEY")
        self.base_url = "https://api.cricketdata.org/v1"
        self._cache = None
        self._last_fetch = 0
        self._cache_expiry = 300 # 5 minutes cache to save credits

    def get_live_scores(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current live matches and filter for India/IPL.
        """
        if not self.api_key:
            return None

        # Return cached data if valid
        if self._cache and (time.time() - self._last_fetch < self._cache_expiry):
            return self._cache

        try:
            max_retries = 2
            data = {"status": "failure"} # Default
            for attempt in range(max_retries):
                try:
                    url = f"{self.base_url}/currentMatches?apikey={self.api_key}"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    break # Success
                except (requests.exceptions.RequestException, ConnectionError, ConnectionResetError) as e:
                    if attempt == max_retries - 1:
                        logger.warning(f"Cricket API Connection Issue (Waiting 60s): {e}")
                        self._last_fetch = time.time() - (self._cache_expiry - 60) # Only lockout for 60s
                        return self._cache
                    time.sleep(1) # Wait 1s before retry
            
            if data.get("status") != "success":
                logger.warning(f"Cricket API Status Alert: {data.get('reason', 'Unknown error')}")
                self._last_fetch = time.time() # Negative caching
                return self._cache # Fallback to stale cache

            matches = data.get("data", [])
            live_india_match = None
            
            # Find the first live India or IPL match
            for m in matches:
                name = m.get("name", "").lower()
                status = m.get("status", "").lower()
                is_live = "live" in status or "started" in status or m.get("matchStarted", False)
                if not is_live: continue
                if "india" in name or "ipl" in name or "indian premier league" in name:
                    live_india_match = m
                    break
            
            if live_india_match:
                result = {
                    "id": live_india_match.get("id"),
                    "name": live_india_match.get("name"),
                    "matchType": live_india_match.get("matchType"),
                    "status": live_india_match.get("status"),
                    "venue": live_india_match.get("venue"),
                    "score": live_india_match.get("score", []),
                    "short_score": self._get_short_score(live_india_match)
                }
                self._cache = result
                self._last_fetch = time.time()
                return result
            
            return None
            
        except Exception as e:
            logger.warning(f"Cricket Service Temporary Failure: {e}")
            self._last_fetch = time.time() # Negative caching
            return self._cache

    def _get_short_score(self, match: Dict[str, Any]) -> str:
        """Helper to create a 1-line score string."""
        scores = match.get("score", [])
        if not scores:
            return "Match Started (Updating...)"
            
        # Example: [{"r": 120, "w": 3, "o": 15.2, "inning": "India Inning 1"}]
        latest = scores[-1]
        runs = latest.get("r", 0)
        wickets = latest.get("w", 0)
        overs = latest.get("o", 0.0)
        inning = latest.get("inning", "")
        
        # Clean up inning name or team name
        team = "Live"
        if "india" in inning.lower() or "india" in match.get("name", "").lower():
            team = "IND"
        elif "ipl" in match.get("name", "").lower():
            # Try to get the batting team from inning string (e.g. "Chennai Super Kings Inning 1")
            match_name = match.get("name", "")
            if " vs " in match_name:
                teams = match_name.split(" vs ")
                # Heuristic: Find which team from the match name is in the inning string
                for t in teams:
                    if t.lower() in inning.lower():
                        team = "".join([w[0] for w in t.split()]).upper() # Initials
                        break

        return f"{team} {runs}/{wickets} ({overs})"

if __name__ == "__main__":
    service = CricketService()
    print(service.get_live_scores())
