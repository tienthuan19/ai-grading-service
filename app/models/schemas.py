from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any

class EssayAnswer(BaseModel):
    question_id: str
    question_text: str
    model_answer: Optional[str] = None
    student_answer: str

    # Cho phép chấm điểm lẻ (8.5, 7.25…)
    weight: float = 100.0

    model_config = ConfigDict(protected_namespaces=())


class GradingRequest(BaseModel):
    submission_id: str
    assignment_id: str
    student_id: str

    file_url: Optional[str] = None

    # FIX BUG list default
    essay_answers: List[EssayAnswer] = Field(default_factory=list)

    submitted_at: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class GradingResult(BaseModel):
    submission_id: str

    # 👇 SỬA DÒNG NÀY: Thêm alias để map sang tên biến bên Java
    score: float = Field(serialization_alias="scoreAi")

    feedback: str
    error: Optional[str] = None
