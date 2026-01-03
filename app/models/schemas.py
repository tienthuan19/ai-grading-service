from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any

class EssayAnswer(BaseModel):
    question_id: str
    question_text: str
    model_answer: Optional[str] = None
    student_answer: str
    weight: int = 100

    # Tắt cảnh báo conflict namespace của Pydantic
    model_config = ConfigDict(protected_namespaces=())

# Đổi SubmissionMessage -> GradingRequest
class GradingRequest(BaseModel):
    submission_id: str
    assignment_id: str
    student_id: str
    file_url: Optional[str] = None
    essay_answers: List[EssayAnswer] = []
    submitted_at: Optional[str] = None
    meta: Optional[dict] = None

# Đổi AIResult -> GradingResult và chuẩn hóa field
class GradingResult(BaseModel):
    submission_id: str
    score: float          # Đổi score_ai -> score cho gọn
    feedback: str
    error: Optional[str] = None