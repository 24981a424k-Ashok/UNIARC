import os
from pathlib import Path
from dotenv import load_dotenv

# Suppress TensorFlow oneDNN info logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

load_dotenv()

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Data Directory - Priority: /app/data (HF), then project-local 'data'
DATA_DIR_ENV = os.getenv("DATA_DIR_PATH")
if DATA_DIR_ENV:
    DATA_DIR = Path(DATA_DIR_ENV)
elif Path("/app/data").exists():
    DATA_DIR = Path("/app/data")
else:
    DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True, parents=True)

from src.utils.secret_manager import SecretManager

# API Keys
NEWS_API_KEY = SecretManager.get("NEWS_API_KEY")
GNEWS_API_KEY = SecretManager.get("GNEWS_API_KEY")
GNEWS_API_KEY_2 = SecretManager.get("GNEWS_API_KEY_2") # Secondary key for higher quota
OPENAI_API_KEY = SecretManager.get("OPENAI_API_KEY")

# NewsData setting
NEWSDATA_API_KEY = SecretManager.get("NEWSDATA_API_KEY")
CRICKET_API_KEY = SecretManager.get("CRICKET_API_KEY")

# Groq API Keys
GROQ_API_KEY = SecretManager.get("GROQ_API_KEY")
GROQ_API_KEYS = [
    SecretManager.get("GROQ_API_KEY_1"),
    SecretManager.get("GROQ_API_KEY_2"),
    SecretManager.get("GROQ_API_KEY_3")
]
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]

# Specialized Groq Keys
GROQ_KEY_TELUGU = SecretManager.get("GROQ_KEY_TELUGU")
GROQ_KEY_HINDI = SecretManager.get("GROQ_KEY_HINDI")
GROQ_KEY_MALAYALAM = SecretManager.get("GROQ_KEY_MALAYALAM")
GROQ_KEY_TAMIL = SecretManager.get("GROQ_KEY_TAMIL")
GROQ_KEY_CRYSTAL_BALL = SecretManager.get("GROQ_KEY_CRYSTAL_BALL")

# Translation Setting
TRANSLATION_KEYS = [
    SecretManager.get("TRANSLATION_OPENAI_KEY_1"),
    SecretManager.get("TRANSLATION_OPENAI_KEY_2"),
    SecretManager.get("TRANSLATION_OPENAI_KEY_3")
]
TRANSLATION_KEYS = [k for k in TRANSLATION_KEYS if k] # Filter out None values

# Firebase Config
FIREBASE_API_KEY = SecretManager.get("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = SecretManager.get("FIREBASE_AUTH_DOMAIN")
FIREBASE_PROJECT_ID = SecretManager.get("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = SecretManager.get("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = SecretManager.get("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID = SecretManager.get("FIREBASE_APP_ID")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/news.db")
VECTOR_DB_PATH = DATA_DIR / "vector_store.index"

# News Setting
NEWS_SOURCES_RSS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
]

# Web Setting
PORT = int(os.getenv("PORT", 7860))
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "06:00")
MIN_CREDIBILITY_SCORE = 0.4  # Lowered from 0.6 for better density
SIMILARITY_THRESHOLD = 0.85
