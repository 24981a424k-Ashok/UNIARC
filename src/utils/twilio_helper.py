import os
from twilio.rest import Client
from loguru import logger

class TwilioHelper:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_NUMBER")
        
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio Client Initialized.")
            except Exception as e:
                logger.error(f"Twilio Init Failed: {e}")

    def send_sms(self, to_number: str, message: str):
        if not self.client:
            logger.warning(f"SMS skipped (Twilio not configured). To: {to_number}, Body: {message}")
            return None
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            logger.info(f"SMS Sent to {to_number}. SID: {msg.sid}")
            return msg.sid
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return None

# Singleton instance
twilio_helper = TwilioHelper()
