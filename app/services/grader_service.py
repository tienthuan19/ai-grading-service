import google.generativeai as genai
import json
import logging
from app.core.config import settings
from app.models.schemas import GradingRequest, GradingResult

logger = logging.getLogger(__name__)

# Setup Google Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class GraderService:
    @staticmethod
    def grade_submission(request: GradingRequest) -> GradingResult:
        try:
            # Prompt kỹ thuật (System Prompt)
            prompt = f"""
            Vai trò: Bạn là giáo viên chấm thi công tâm.
            Nhiệm vụ: Chấm điểm bài làm dựa trên thông tin sau:
            - Câu hỏi: {request.question_content}
            - Đáp án mẫu: {request.model_answer if request.model_answer else "Không có, tự đánh giá theo kiến thức chuẩn."}
            - Bài làm học sinh: {request.student_answer}
            - Thang điểm tối đa: {request.max_score}

            Yêu cầu bắt buộc:
            1. Output duy nhất là một JSON object hợp lệ. Không thêm markdown ```json.
            2. Format: {{"score": <số thực>, "feedback": "<nhận xét ngắn gọn>"}}
            3. Điểm số không được vượt quá {request.max_score}.
            """

            response = model.generate_content(prompt)

            # Xử lý text trả về (Cleaning)
            raw_text = response.text.strip()
            # Đôi khi AI vẫn thêm markdown, ta lọc bỏ
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()

            data = json.loads(raw_text)

            # Validate điểm số
            score = float(data.get("score", 0))
            if score > request.max_score: score = request.max_score
            if score < 0: score = 0

            return GradingResult(
                submission_id=request.submission_id,
                score=score,
                feedback=data.get("feedback", "Đã chấm xong.")
            )

        except Exception as e:
            logger.error(f"Lỗi chấm bài {request.submission_id}: {str(e)}")
            return GradingResult(
                submission_id=request.submission_id,
                score=0,
                feedback="Lỗi hệ thống chấm điểm AI.",
                error=str(e)
            )