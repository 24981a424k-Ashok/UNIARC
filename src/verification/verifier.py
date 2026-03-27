import logging
import os
import time
from typing import List, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.database.models import RawNews, VerifiedNews
from src.config.settings import MIN_CREDIBILITY_SCORE

logger = logging.getLogger(__name__)

# Global flag to avoid repeated failed import attempts
_SBERT_INITIALIZED = False
_HAS_SBERT = False

def _check_sbert():
    global _SBERT_INITIALIZED, _HAS_SBERT
    if _SBERT_INITIALIZED:
        return _HAS_SBERT
    
    try:
        import sentence_transformers
        _HAS_SBERT = True
    except Exception:
        _HAS_SBERT = False
    
    _SBERT_INITIALIZED = True
    return _HAS_SBERT

# Global cache for the transformer model to avoid redundant loading
_CACHED_MODEL = None

class VerificationEngine:
    def __init__(self, use_strict_mode: bool = False):
        self.use_strict_mode = use_strict_mode
        self.credibility_map = {
            "bbc-news": 0.95,
            "reuters": 0.95,
            "associated-press": 0.95,
            "techcrunch": 0.85,
            "the-verge": 0.80,
            "cnn": 0.85,
            "wired": 0.82,
            "arstechnica": 0.85, 
            "engadget": 0.75,
            "fox-news": 0.70,
            "google-news": 0.60,
            "ndtv": 0.75,
            "times-of-india": 0.75,
            "the-hindu": 0.90,
            "x": 0.85,
            "twitter": 0.85,
            "generic": 0.4
        }
        
        global _CACHED_MODEL
        self.model = _CACHED_MODEL
        
        # Check if SBERT is enabled via environment (default to True unless on constrained environment)
        # Hugging Face usually provides 'SPACE_ID', we can use that for auto-detection
        enable_sbert = os.getenv("ENABLE_SBERT", "true").lower() == "true"
        is_huggingface = os.getenv("SPACE_ID") is not None
        
        if is_huggingface and os.getenv("ENABLE_SBERT") is None:
            logger.info("Running on Hugging Face Space. Disabling heavy Intelligence Engine to save RAM.")
            enable_sbert = False

        if enable_sbert and self.model is None and _check_sbert():
            try:
                from sentence_transformers import SentenceTransformer
                # Load a lightweight model
                logger.info("Initializing Intelligence Engine (SentenceTransformer)... this may take a moment.")
                _CACHED_MODEL = SentenceTransformer('all-MiniLM-L6-v2') 
                self.model = _CACHED_MODEL
                logger.info("Intelligence Engine active.")
            except Exception as e:
                logger.error(f"Failed to load Intelligence Engine: {e}")
                self.model = None
        elif not enable_sbert:
            logger.info("Intelligence Engine (SBERT) is disabled via configuration.")
            self.model = None

    def verify_batch(self, session: Session, article_ids: List[int]) -> int:
        """
        Process a batch of raw news articles, verify them, and promote to VerifiedNews.
        Returns count of verified articles.
        """
        verified_count = 0
        
        # Cache existing verified titles/embeddings from the last 2 days to compare
        # (For SBERT, we would ideally compute embeddings for all and do matrix search, 
        # but for this batch size, loop is okay or we can encode verified list once)
        cutoff = datetime.utcnow() - timedelta(days=2)
        existing_news = session.query(VerifiedNews).filter(VerifiedNews.published_at >= cutoff).all()
        
        # Simple text cache for Jaccard/exact match as fallback
        existing_titles = [n.title for n in existing_news]
        existing_embeddings = None
        
        if self.model and existing_news:
             existing_texts = [n.title + " " + (n.content[:200] if n.content else "") for n in existing_news]
             if existing_texts:
                existing_embeddings = self.model.encode(existing_texts, convert_to_tensor=True)

        for art_id in article_ids:
            article = session.query(RawNews).filter(RawNews.id == art_id).first()
            if not article:
                continue
            
            # --- 1. Credibility Check ---
            source_id = article.source_id or "generic"
            # Normalize source_id if needed
            lookup_id = source_id.split('-')[0] if '-' in source_id else source_id
            score = self.credibility_map.get(lookup_id, self.credibility_map.get(source_id, self.credibility_map["generic"]))
            
            # Boost score for government/reputable domains
            if article.url and ("gov" in article.url or "edu" in article.url):
                score = 1.0
            
            article.verification_score = score
            article.is_verified = score >= MIN_CREDIBILITY_SCORE
            
            if not article.is_verified:
                article.processed = True
                continue

            # --- 2. Deduplication ---
            is_dupe = False
            
            # A. Exact Title/URL Match (handled partly in collection, but good to be safe)
            if article.title in existing_titles:
                is_dupe = True
                logger.info(f"Duplicate found (Exact Title): {article.title}")

            # B. Semantic Similarity
            if not is_dupe and self.model and existing_embeddings is not None and len(existing_embeddings) > 0:
                try:
                    from sentence_transformers import util
                    text_to_check = article.title + " " + (article.content[:200] if article.content else "")
                    new_emb = self.model.encode(text_to_check, convert_to_tensor=True)
                    
                    # Compute cosine similarities
                    cosine_scores = util.cos_sim(new_emb, existing_embeddings)
                    
                    # Find best match
                    best_score = cosine_scores.max().item()
                    
                    if best_score > 0.85: # Threshold for "same story"
                        is_dupe = True
                        logger.info(f"Duplicate found (Semantic {best_score:.2f}): {article.title}")
                except Exception as e:
                    logger.warning(f"Semantic deduplication failed: {e}")

            if is_dupe:
                article.processed = True
                # We could mark it as 'duplicate' in DB if we had a status field
                continue

            # --- 3. Promote to VerifiedNews ---
            verified_news = VerifiedNews(
                raw_news_id=article.id,
                title=article.title,
                content=article.content or article.description or "",
                published_at=article.published_at,
                credibility_score=score,
                category="General",
                country=article.country
            )
            session.add(verified_news)
            
            # Update local cache for next item in THIS batch
            existing_titles.append(article.title)
            # (Updating embeddings iteratively is complex without re-stacking, skipping for this iteration)
            
            verified_count += 1
            article.processed = True
        
        try:
            session.commit()
            return verified_count
        except Exception as e:
            logger.error(f"Error during verification batch: {e}")
            session.rollback()
            return 0
