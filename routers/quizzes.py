from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal
from models import CompatibilityQuiz, UserQuizResult, User, UserProfile
from auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.get("/")
async def get_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available quizzes"""
    # Check if user has premium
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
    
    query = db.query(CompatibilityQuiz)
    if not has_premium:
        query = query.filter(CompatibilityQuiz.premium == False)
    
    quizzes = query.all()
    return {
        "quizzes": [
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "premium": q.premium,
                "questions_count": len(json.loads(q.questions)) if q.questions else 0
            }
            for q in quizzes
        ]
    }

@router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific quiz with questions"""
    quiz = db.query(CompatibilityQuiz).filter(CompatibilityQuiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check premium access
    if quiz.premium:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
        if not has_premium:
            raise HTTPException(status_code=403, detail="Premium subscription required")
    
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "questions": json.loads(quiz.questions) if quiz.questions else [],
        "premium": quiz.premium
    }

class QuizSubmission(BaseModel):
    quiz_id: int
    answers: dict

@router.post("/submit")
async def submit_quiz(
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit quiz answers and calculate score"""
    quiz = db.query(CompatibilityQuiz).filter(CompatibilityQuiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Simple scoring logic (can be enhanced)
    score = len(submission.answers) * 10  # 10 points per question answered
    
    result = UserQuizResult(
        user_id=current_user.id,
        quiz_id=submission.quiz_id,
        answers=json.dumps(submission.answers),
        score=score
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return {
        "id": result.id,
        "score": result.score,
        "message": "Quiz submitted successfully",
        "insights": f"You scored {score} points! This indicates your compatibility preferences."
    }

@router.get("/my/results")
async def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's quiz results"""
    results = db.query(UserQuizResult).filter(
        UserQuizResult.user_id == current_user.id
    ).order_by(UserQuizResult.completed_at.desc()).all()
    
    return {
        "results": [
            {
                "id": r.id,
                "quiz_id": r.quiz_id,
                "score": r.score,
                "completed_at": r.completed_at.isoformat()
            }
            for r in results
        ]
    }
