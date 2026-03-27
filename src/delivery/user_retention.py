from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from src.database.models import SessionLocal, User, Folder, SavedArticle, ReadHistory, VerifiedNews
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(tags=["Retention"], prefix="/api/retention")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    
    # Track the reading event
    history_entry = ReadHistory(
        user_id=user.id,
        news_id=payload.news_id
    )
    db.add(history_entry)
    db.commit()
    return {"status": "success", "message": "History tracked"}

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
