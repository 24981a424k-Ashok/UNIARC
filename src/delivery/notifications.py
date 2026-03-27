from typing import List
from firebase_admin import messaging
from loguru import logger
from sqlalchemy.orm import Session
from src.database.models import User, Subscription

class NotificationManager:
    @staticmethod
    def send_push_notification(tokens: List[str], title: str, body: str, data: dict = None):
        """Send a multicast message to multiple device tokens."""
        if not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            tokens=tokens
        )
        try:
            # send_multicast is deprecated/removed in some versions, using send_each_for_multicast
            # Depending on firebase-admin version, one might work better.
            if hasattr(messaging, 'send_each_for_multicast'):
                response = messaging.send_each_for_multicast(message)
                logger.info(f"Successfully sent {response.success_count} notifications; {response.failure_count} failed.")
            else:
                response = messaging.send_multicast(message)
                logger.info(f"Successfully sent {response.success_count} notifications; {response.failure_count} failed.")
        except Exception as e:
            logger.error(f"FCM Multicast failed: {e}")

    @staticmethod
    def send_email(email: str, title: str, body: str):
        """Stub for sending Email notifications."""
        if not email: return
        logger.info(f"[EMAIL STUB] Sending to {email}: {title} - {body[:50]}...")
        # Integration point for SendGrid/AWS SES/etc.

    @staticmethod
    def send_sms(phone: str, body: str):
        """Stub for sending SMS notifications."""
        if not phone: return
        logger.info(f"[SMS STUB] Sending to {phone}: {body[:50]}...")
        # Integration point for Twilio/SNS/etc.

    @staticmethod
    def notify_subscribers(db: Session, category: str, news_title: str, news_url: str):
        """Find users subscribed to a category and notify them via all available channels."""
        subscribers = db.query(User).join(Subscription).filter(
            (Subscription.category == category) | (Subscription.category == "All")
        ).all()

        push_tokens = [u.push_token for u in subscribers if u.push_token]
        
        # 1. FCM Push
        if push_tokens:
            NotificationManager.send_push_notification(
                tokens=push_tokens,
                title=f"New in {category}",
                body=news_title,
                data={"url": news_url}
            )

        # 2. Email & SMS
        for user in subscribers:
            if user.email:
                NotificationManager.send_email(user.email, f"AI News: {category}", f"{news_title}\nRead more: {news_url}")
            if user.phone:
                NotificationManager.send_sms(user.phone, f"AI News [{category}]: {news_title}. {news_url}")
    @staticmethod
    def send_daily_brief(db: Session, brief_list: List[dict]):
        """Send the 60-second brief to all users."""
        if not brief_list:
            return

        body = "\n".join([f"• {b['title']}" for b in brief_list[:5]])
        users = db.query(User).filter(User.push_token != None).all()
        push_tokens = [u.push_token for u in users]

        if push_tokens:
            NotificationManager.send_push_notification(
                tokens=push_tokens,
                title="⭐ Today's 60-Second Brief",
                body=body,
                data={"type": "brief"}
            )
            logger.info("Daily brief sent to subscribers.")
