from pydantic import BaseModel
from typing import List, Optional, Any

class EssayAnswer(BaseModel):
    question_id: str  # Sửa int thành str
    question_text: str
    model_answer: Optional[str] = None
    student_answer: str
    weight: int = 100

class SubmissionMessage(BaseModel):
    submission_id: str
    assignment_id: str # Sửa int thành str
    student_id: str    # Sửa int thành str

    file_url: Optional[str] = None
    essay_answers: List[EssayAnswer] = []
    submitted_at: Optional[str] = None
    meta: Optional[dict] = None

class AIResult(BaseModel):
    submission_id: str
    score_ai: Optional[float] = None # Nên để float vì điểm có thể lẻ
    feedback: Optional[str] = None
    confidence: Optional[float] = None
    summary_raw: Optional[Any] = None