import os
import logging
from datetime import datetime, timedelta
from twilio.rest import Client
from sqlalchemy.orm import Session
from src.database.models import SessionLocal, TopicTracking, VerifiedNews, User, TrackNotification
from src.config.settings import getattr

logger = logging.getLogger(__name__)

# Twilio Config from ENV
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SENDER = os.getenv("TWILIO_NUMBER")

class NotifierService:
    def __init__(self):
        self.enabled = all([TWILIO_SID, TWILIO_TOKEN, TWILIO_SENDER])
        if self.enabled:
            self.client = Client(TWILIO_SID, TWILIO_TOKEN)
            logger.info("Twilio Notifier initialized.")
        else:
            logger.warning("Twilio Notifier disabled: Missing credentials in .env")

    def send_sms(self, to_phone: str, message: str):
        if not self.enabled:
            return False
            
        try:
            # Ensure phone starts with +
            if not to_phone.startswith("+"):
                logger.warning(f"Phone {to_phone} lacks country code. SMS might fail.")
            
            self.client.messages.create(
                body=message,
                from_=TWILIO_SENDER,
                to=to_phone
            )
            logger.info(f"SMS sent to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return False

    def scan_and_notify_topics(self):
        """
        Scans recently added VerifiedNews and matches them against user TopicTracking.
        """
        db = SessionLocal()
        try:
            # 1. Get new news from the last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_news = db.query(VerifiedNews).filter(VerifiedNews.created_at >= one_hour_ago).all()
            
            if not recent_news:
                return
            
            # 2. Get active tracking entries
            # Tracking lasts 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_tracks = db.query(TopicTracking).filter(TopicTracking.created_at >= thirty_days_ago).all()
            
            for track in active_tracks:
                user = track.user
                if not user or not user.phone:
                    continue
                
                # Check for matches
                for news in recent_news:
                    # Match by keyword
                    match = False
                    for kw in (track.topic_keywords or []):
                        if kw.lower() in news.title.lower() or kw.lower() in news.content.lower():
                            match = True
                            break
                    
                    if match:
                        # Check if already notified for this article
                        existing = db.query(TrackNotification).filter(
                            TrackNotification.user_id == user.id,
                            TrackNotification.news_id == news.id
                        ).first()
                        
                        if not existing:
                            # Send SMS
                            msg = f"UNI INTEL Alert: New article matches your tracked topic!\n\n{news.title}\nRead more: http://localhost:8000/dashboard?id={news.id}"
                            success = self.send_sms(user.phone, msg)
                            
                            if success:
                                notification = TrackNotification(user_id=user.id, news_id=news.id)
                                db.add(notification)
                                db.commit()
                                logger.info(f"Notified user {user.id} for article {news.id}")
                                
        except Exception as e:
            logger.error(f"Error during topic scan: {e}")
        finally:
            db.close()

notifier_service = NotifierService()
