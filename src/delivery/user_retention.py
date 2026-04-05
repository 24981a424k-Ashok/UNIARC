from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from src.database.models import SessionLocal, User, Folder, SavedArticle, ReadHistory, VerifiedNews, TopicTracking
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Retention"], prefix="/api/user")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status")
async def get_user_status(firebase_uid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        # Create user if missing (first login)
        user = User(firebase_uid=firebase_uid)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Calculate history map for calendar
    history = db.query(ReadHistory).filter(ReadHistory.user_id == user.id).all()
    history_map = {h.read_at.date().isoformat(): True for h in history}
    
    return {
        "status": "success",
        "current_streak": user.current_streak,
        "best_streak": getattr(user, 'best_streak', user.current_streak),
        "phone": user.phone,
        "history": history_map
    }

@router.post("/ping_streak")
async def ping_streak(payload: dict = Body(...), db: Session = Depends(get_db)):
    firebase_uid = payload.get("firebase_uid")
    if not firebase_uid:
        raise HTTPException(status_code=422, detail="firebase_uid required")
        
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        user = User(firebase_uid=firebase_uid)
        db.add(user)
        db.commit()
        db.refresh(user)

    today = datetime.utcnow().date()
    last_active = user.last_active_date.date() if user.last_active_date else None
    
    milestone_hit = None
    if not last_active:
        user.current_streak = 1
    elif last_active == today:
        pass # Already active
    elif last_active == today - timedelta(days=1):
        user.current_streak += 1
        # Simple Milestone Logic
        if user.current_streak in [7, 30, 100]:
            milestone_hit = user.current_streak
    else:
        user.current_streak = 1
        
    user.last_active_date = datetime.utcnow()
    db.commit()
    
    return {
        "status": "success", 
        "current_streak": user.current_streak,
        "milestone_hit": milestone_hit
    }

class SaveRequest(BaseModel):
    firebase_uid: str
    news_id: int
    folder_id: Optional[int] = None

class FolderRequest(BaseModel):
    firebase_uid: str
    name: str

class HistoryRequest(BaseModel):
    firebase_uid: str
    news_id: int

@router.post("/save")
async def save_article(payload: SaveRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == payload.firebase_uid).first()
    if not user:
        logger.warning(f"User {payload.firebase_uid} not found during save. Creating lazy entry.")
        user = User(firebase_uid=payload.firebase_uid)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Check if already saved
    existing = db.query(SavedArticle).filter(
        SavedArticle.user_id == user.id,
        SavedArticle.news_id == payload.news_id
    ).first()
    
    if existing:
        return {"status": "already_saved", "message": "Article already in saves"}
    
    save_entry = SavedArticle(
        user_id=user.id,
        news_id=payload.news_id,
        folder_id=payload.folder_id
    )
    db.add(save_entry)
    db.commit()
    return {"status": "success", "message": "Article saved"}

@router.post("/history")
async def track_history(payload: HistoryRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == payload.firebase_uid).first()
    if not user:
        # Lazy creation of user if they exist in Firebase but not in our DB
        # This can happen if the /api/login call was skipped or failed
        logger.warning(f"User {payload.firebase_uid} not found during history track. Creating lazy entry.")
        user = User(firebase_uid=payload.firebase_uid)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 71. Track the reading event - but only once per article per day for streak
    existing_history = db.query(ReadHistory).filter(
        ReadHistory.user_id == user.id,
        ReadHistory.news_id == payload.news_id,
        ReadHistory.read_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).first()

    if not existing_history:
        history_entry = ReadHistory(
            user_id=user.id,
            news_id=payload.news_id
        )
        db.add(history_entry)
        
        # --- STREAK LOGIC ---
        today = datetime.utcnow().date()
        last_active = user.last_active_date.date() if user.last_active_date else None
        
        if not last_active:
             user.current_streak = 1
        elif last_active == today:
             # Already active today, streak stays
             pass
        elif last_active == today - timedelta(days=1):
             # Consecutive day, increment streak
             user.current_streak += 1
             logger.info(f"Streak Increased! User {user.id} now on {user.current_streak} days.")
        else:
             # Streak broken, reset
             user.current_streak = 1
             logger.info(f"Streak Broken. User {user.id} reset to 1.")
        
        user.last_active_date = datetime.utcnow()
    
    db.commit()
    return {"status": "success", "message": "History tracked", "streak": user.current_streak}

@router.get("/saved/{firebase_uid}")
async def get_saved_articles(firebase_uid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    saves = db.query(SavedArticle).filter(SavedArticle.user_id == user.id).all()
    result = []
    for s in saves:
        news = s.news
        if not news:
            continue
        result.append({
            "id": news.id,
            "title": news.title,
            "source": news.raw_news.source_name if news.raw_news else "Unknown",
            "category": news.category,
            "saved_at": s.saved_at.isoformat(),
            "url": news.raw_news.url if news.raw_news else "#"
        })
    return result

@router.get("/history/{firebase_uid}")
async def get_history(firebase_uid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = db.query(ReadHistory).filter(ReadHistory.user_id == user.id).order_by(ReadHistory.read_at.desc()).all()
    result = []
    for h in history:
        news = h.news
        if not news:
            continue
        result.append({
            "id": news.id,
            "title": news.title,
            "source": news.raw_news.source_name if news.raw_news else "Unknown",
            "read_at": h.read_at.isoformat(),
            "url": news.raw_news.url if news.raw_news else "#"
        })
    return result

@router.delete("/history/{firebase_uid}")
async def clear_history(firebase_uid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.query(ReadHistory).filter(ReadHistory.user_id == user.id).delete()
    db.commit()
    return {"status": "success", "message": "History cleared"}

@router.delete("/saved/{firebase_uid}")
async def clear_saved_articles(firebase_uid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.query(SavedArticle).filter(SavedArticle.user_id == user.id).delete()
    db.commit()
    return {"status": "success", "message": "Saved articles cleared"}

@router.post("/folders")
async def create_folder(payload: FolderRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == payload.firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    folder = Folder(user_id=user.id, name=payload.name)
    db.add(folder)
    db.commit()
    return {"status": "success", "folder_id": folder.id}

class PhoneUpdateRequest(BaseModel):
    firebase_uid: str
    phone: str

class TrackTopicRequest(BaseModel):
    firebase_uid: str
    news_id: Optional[int] = None
    keywords: List[str]

@router.post("/update_phone")
async def update_phone(payload: PhoneUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == payload.firebase_uid).first()
    if not user:
        user = User(firebase_uid=payload.firebase_uid)
        db.add(user)
    
    user.phone = payload.phone
    db.commit()
    return {"status": "success", "message": "Phone updated"}

@router.post("/track_topic")
async def track_topic(payload: TrackTopicRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.firebase_uid == payload.firebase_uid).first()
    if not user:
        user = User(firebase_uid=payload.firebase_uid)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create topic tracking entry
    track_entry = TopicTracking(
        user_id=user.id,
        news_id=payload.news_id,
        topic_keywords=payload.keywords,
        language=user.preferred_language or "english",
        notify_sms=True
    )
    db.add(track_entry)
    db.commit()
    
    return {"status": "success", "message": "Topic tracked for 30 days"}
