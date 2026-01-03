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
class GradingDetail(BaseModel):
    # 👇 CHO PHÉP DÙNG TÊN BIẾN PYTHON (question_id) ĐỂ TẠO OBJECT
    model_config = ConfigDict(populate_by_name=True)

    # Dùng alias="questionId" để định danh tên field cho cả input lẫn output
    questionId: str = Field(alias="questionId")
    score: float
    feedback: str

class GradingResult(BaseModel):
    # 👇 QUAN TRỌNG: Cấu hình này giúp fix lỗi "Field required"
    model_config = ConfigDict(populate_by_name=True)

    submissionId: str = Field(alias="submissionId")

    # scoreAi là tên field Java mong đợi
    score: float = Field(alias="scoreAi")

    feedback: str

    details: List[GradingDetail] = Field(default_factory=list)

    error: Optional[str] = None



