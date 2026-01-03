from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any

class EssayAnswer(BaseModel):
    question_id: str
    question_text: str
    model_answer: Optional[str] = None
    student_answer: str
    weight: float = 100.0

    model_config = ConfigDict(protected_namespaces=())

class GradingRequest(BaseModel):
    submission_id: str
    assignment_id: str
    student_id: str
    file_url: Optional[str] = None
    essay_answers: List[EssayAnswer] = Field(default_factory=list)
    submitted_at: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class GradingDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # SỬA: Đổi tên biến Python thành snake_case (question_id)
    # Alias giữ nguyên là "questionId" để mapping với JSON bên ngoài
    question_id: str = Field(alias="questionId")
    score: float
    feedback: str

class GradingResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # SỬA: Đổi tên biến Python thành snake_case (submission_id)
    submission_id: str = Field(alias="submissionId")

    # scoreAi là tên field Java mong đợi
    score: float = Field(alias="scoreAi")

    feedback: str

    details: List[GradingDetail] = Field(default_factory=list)

    error: Optional[str] = None