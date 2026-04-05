from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Base logic moved to database.py

Base = declarative_base()

class RawNews(Base):
    __tablename__ = "raw_news"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True)
    source_name = Column(String)
    author = Column(String, nullable=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    url = Column(String, unique=True, index=True)
    url_to_image = Column(String, nullable=True)
    published_at = Column(DateTime)
    content = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata for processing status
    is_verified = Column(Boolean, default=False)
    verification_score = Column(Float, default=0.0)
    processed = Column(Boolean, default=False)
    country = Column(String, nullable=True, index=True)

class VerifiedNews(Base):
    __tablename__ = "verified_news"

    id = Column(Integer, primary_key=True, index=True)
    raw_news_id = Column(Integer, ForeignKey("raw_news.id"))
    title = Column(String)
    content = Column(Text)
    summary_bullets = Column(JSON) # List of strings
    
    # Analysis Fields
    analysis = Column(JSON, nullable=True) # Flexible storage for extra metadata
    impact_tags = Column(JSON) # e.g. ["Jobs", "Market"]
    bias_rating = Column(String) # e.g. "Neutral", "Slightly Biased"
    
    category = Column(String, index=True)
    country = Column(String, nullable=True, index=True)
    credibility_score = Column(Float)
    impact_score = Column(Integer) # 1-10
    why_it_matters = Column(Text)
    who_is_affected = Column(Text, nullable=True)
    short_term_impact = Column(Text, nullable=True)
    long_term_impact = Column(Text, nullable=True)
    sentiment = Column(String)
    
    is_fake = Column(Boolean, default=False)
    flag_count = Column(Integer, default=0)
    
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    raw_news = relationship("RawNews")

    @property
    def image_url(self) -> Optional[str]:
        """Backward compatibility for templates and logic expecting image_url attribute."""
        if self.raw_news and self.raw_news.url_to_image:
            return self.raw_news.url_to_image
        return None

    @property
    def url(self) -> str:
        """Helper to access the source URL."""
        if self.raw_news:
            return self.raw_news.url
        return "#"

    @property
    def source_name(self) -> str:
        """Helper to access the source name."""
        if self.raw_news:
            return self.raw_news.source_name
        return "Unknown"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary_bullets": self.summary_bullets,
            "analysis": self.analysis,
            "impact_tags": self.impact_tags,
            "bias_rating": self.bias_rating,
            "category": self.category,
            "country": self.country,
            "credibility_score": self.credibility_score,
            "impact_score": self.impact_score,
            "why_it_matters": self.why_it_matters,
            "who_is_affected": self.who_is_affected,
            "short_term_impact": self.short_term_impact,
            "long_term_impact": self.long_term_impact,
            "sentiment": self.sentiment,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source_name": self.raw_news.source_name if self.raw_news else "Unknown"
        }

class DailyDigest(Base):
    __tablename__ = "daily_digests"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    content_json = Column(JSON) # Full structured digest
    is_published = Column(Boolean, default=False)

class TopicTracking(Base):
    __tablename__ = "topic_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    news_id = Column(Integer, ForeignKey("verified_news.id"), nullable=True)
    topic_keywords = Column(JSON) # ["AI", "Nvidia"]
    language = Column(String, default="english")
    notify_sms = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tracked_topics")
    news = relationship("VerifiedNews")

class TrackNotification(Base):
    __tablename__ = "track_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    news_id = Column(Integer, ForeignKey("verified_news.id"))
    notified_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    news = relationship("VerifiedNews")

class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)
    otp_code = Column(String)
    expires_at = Column(DateTime)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    push_token = Column(String, nullable=True)
    bounty_points = Column(Integer, default=0)
    preferred_language = Column(String, default="english")
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String, nullable=True)
    
    # Premium Streak & Rewards
    current_streak = Column(Integer, default=0)
    streak_history = Column(JSON, default=dict) # e.g. {"2026-04-04": "success", "2026-04-03": "missed"}
    subscription_status = Column(String, default="free") # "free", "premium_eligible", "activated"
    
    last_active_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user")
    folders = relationship("Folder", back_populates="user")
    saved_articles = relationship("SavedArticle", back_populates="user")
    read_history = relationship("ReadHistory", back_populates="user")
    tracked_topics = relationship("TopicTracking", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String) # e.g. "Technology", "All"
    
    user = relationship("User", back_populates="subscriptions")

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="folders")
    saved_articles = relationship("SavedArticle", back_populates="folder")

class SavedArticle(Base):
    __tablename__ = "saved_articles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    news_id = Column(Integer, ForeignKey("verified_news.id"))
    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_articles")
    folder = relationship("Folder", back_populates="saved_articles")
    news = relationship("VerifiedNews")

class ReadHistory(Base):
    __tablename__ = "read_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    news_id = Column(Integer, ForeignKey("verified_news.id"))
    read_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="read_history")
    news = relationship("VerifiedNews")

class FlaggedArticle(Base):
    __tablename__ = "flagged_articles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    news_id = Column(Integer, ForeignKey("verified_news.id"))
    reason = Column(String, nullable=True)
    flagged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    news = relationship("VerifiedNews")

class BreakingNews(Base):
    __tablename__ = "breaking_news"
    
    id = Column(Integer, primary_key=True, index=True)
    verified_news_id = Column(Integer, ForeignKey("verified_news.id"))
    classification = Column(String)  # Breaking News, Developing News, Top Headline
    breaking_headline = Column(String)
    what_happened = Column(JSON)  # List of bullet points
    why_matters = Column(Text)
    next_updates = Column(JSON)  # List of possible next updates
    confidence_level = Column(String)  # High, Medium, Low
    impact_score = Column(Integer)  # 1-10
    recency_minutes = Column(Integer)
    url = Column(String, nullable=True) # Direct access for performance
    image_url = Column(String, nullable=True) # Cached image link
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    verified_news = relationship("VerifiedNews")

class Advertisement(Base):
    __tablename__ = "advertisements"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    position = Column(String, default="both") # "left", "right", "both", "mobile"
    target_node = Column(String, default="Global")
    target_url = Column(String, nullable=True)
    target_platform = Column(String, default="both") # "main", "student", "both"
    created_at = Column(DateTime, default=datetime.utcnow)

class Newspaper(Base):
    __tablename__ = "newspapers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    logo_text = Column(String, nullable=True) # e.g. "NYT"
    logo_color = Column(String, nullable=True) # e.g. "#000000"
    country = Column(String, default="Global")
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemSecret(Base):
    __tablename__ = "system_secrets"
    
    key = Column(String, primary_key=True, index=True) # e.g. "OPENAI_API_KEY"
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProtocolHistory(Base):
    __tablename__ = "protocol_history"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False) # e.g. 'deploy', 'delete', 'register'
    target_type = Column(String, nullable=False) # e.g. 'article', 'source', 'ad'
    target_id = Column(String, nullable=True)
    admin_user = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
from .database import engine, SessionLocal

def init_db():
    Base.metadata.create_all(bind=engine)
