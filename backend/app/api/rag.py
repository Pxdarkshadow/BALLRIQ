"""
RAG FastAPI Router: Grounded Question-Answering Endpoints.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.app.rag.engine import BALLRIQRAGEngine

router = APIRouter(prefix="/api/rag", tags=["rag"])
rag_engine = BALLRIQRAGEngine()


class AskRequest(BaseModel):
    question: str
    match_id: Optional[str] = ""
    language: Optional[str] = "auto"


@router.post("/ask")
async def ask_ballriq(req: AskRequest):
    """Grounded RAG answer with always-present ``citations`` and ``sources``."""
    return rag_engine.answer_question(
        question=req.question,
        match_id=req.match_id if req.match_id else None,
        language=req.language or "auto"
    )


@router.get("/suggested-questions/{match_id}")
async def suggested_questions(match_id: str):
    """Pre-populated queries in English, Hindi, and Marathi."""
    return {
        "match_id": match_id,
        "questions": {
            "en": [
                "Who was the top scorer in this match?",
                "What was the turning point of the match?",
                "How did the powerplay overs go?",
                "Which bowler had the best economy rate?",
                "Describe the final over of the match."
            ],
            "hi": [
                "इस मैच में सबसे महत्वपूर्ण विकेट कौन सा था?",
                "कोहली ने कितने चौके और छक्के लगाए?",
                "पावरप्ले में टीम का प्रदर्शन कैसा रहा?",
                "बुमराह ने किस ओवर में विकेट लिया?",
                "मैच का सबसे बड़ा टर्निंग पॉइंट क्या था?"
            ],
            "mr": [
                "या सामन्यात कोहलीने किती धावा केल्या?",
                "सामन्यातील सर्वात महत्त्वाची विकेट कोणती होती?",
                "पॉवरप्लेमध्ये संघाची कामगिरी कशी होती?",
                "बुमराहने कोणत्या षटकात विकेट घेतली?",
                "सामन्याचा टर्निंग पॉईंट कोणता होता?"
            ]
        }
    }
