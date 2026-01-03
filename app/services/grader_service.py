import json
import logging
import time
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.schemas import GradingRequest, GradingResult

logger = logging.getLogger(__name__)

# Khởi tạo Client
client = genai.Client(api_key=settings.GOOGLE_API_KEY)

class GraderService:
    @staticmethod
    def grade_submission(request: GradingRequest) -> GradingResult:
        total_score = 0.0
        feedback_parts = []

        # --- [FIX LỖI 404] ---
        # Sử dụng phiên bản cụ thể "gemini-1.5-flash-001" thay vì alias
        # Hoặc bạn có thể thử "gemini-2.0-flash" nếu muốn dùng bản mới nhất
        model_id = "gemini-1.5-flash-001"
        # ---------------------

        try:
            for index, answer in enumerate(request.essay_answers, 1):
                logger.info(f"Đang chấm câu hỏi {index}/{len(request.essay_answers)} của bài {request.submission_id}")

                prompt = f"""
                Bạn là giáo viên chấm thi. Hãy chấm điểm câu hỏi sau đây:
                - Câu hỏi: {answer.question_text}
                - Đáp án mẫu: {answer.model_answer if answer.model_answer else "Không có, tự đánh giá theo kiến thức chuẩn."}
                - Bài làm học sinh: {answer.student_answer}
                - Điểm tối đa của câu này: {answer.weight}

                Yêu cầu Output:
                Trả về duy nhất 1 JSON object (không markdown):
                {{"score": <số thực, tối đa {answer.weight}>, "feedback": "<nhận xét ngắn gọn>"}}
                """

                try:
                    # Gọi API với cấu hình JSON response
                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                    raw_text = response.text.strip()
                    # Xử lý trường hợp AI vẫn trả về markdown dù đã config JSON
                    if raw_text.startswith("```"):
                        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

                    data = json.loads(raw_text)

                    q_score = float(data.get("score", 0))
                    # Validate điểm số
                    if q_score > answer.weight: q_score = answer.weight
                    if q_score < 0: q_score = 0

                    q_feedback = data.get("feedback", "")

                    total_score += q_score
                    feedback_parts.append(f"Câu {index}: {q_feedback} ({q_score}/{answer.weight}đ)")

                except Exception as e:
                    logger.error(f"Lỗi chấm câu {answer.question_id}: {e}")
                    feedback_parts.append(f"Câu {index}: Lỗi chấm điểm AI ({e})")

                # Nghỉ 4s để tránh Rate Limit (429)
                time.sleep(4)

            final_feedback = "\n".join(feedback_parts)

            return GradingResult(
                submission_id=request.submission_id,
                score=total_score,
                feedback=final_feedback
            )

        except Exception as e:
            logger.error(f"Lỗi hệ thống chấm bài {request.submission_id}: {str(e)}")
            return GradingResult(
                submission_id=request.submission_id,
                score=0,
                feedback="Lỗi hệ thống nghiêm trọng khi xử lý bài nộp.",
                error=str(e)
            )