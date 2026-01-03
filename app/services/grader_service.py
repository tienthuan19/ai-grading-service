import json
import logging
import time

from google.genai import Client, types

from app.core.config import settings
from app.models.schemas import GradingRequest, GradingResult

logger = logging.getLogger(__name__)

# ✅ Init client đúng SDK
client = Client(api_key=settings.GOOGLE_API_KEY)


class GraderService:
    @staticmethod
    def grade_submission(request: GradingRequest) -> GradingResult:
        total_score: float = 0.0
        feedback_parts: list[str] = []

        # ✅ MODEL HỢP LỆ – ĐÃ SUPPORT generateContent
        model_id = "gemini-1.5-pro"

        try:
            for index, answer in enumerate(request.essay_answers, start=1):
                logger.info(
                    f"Đang chấm câu hỏi {index}/{len(request.essay_answers)} "
                    f"của bài {request.submission_id}"
                )

                prompt = f"""
Bạn là giáo viên chấm thi.

Câu hỏi:
{answer.question_text}

Đáp án mẫu:
{answer.model_answer or "Không có, tự đánh giá theo kiến thức chuẩn."}

Bài làm học sinh:
{answer.student_answer}

Điểm tối đa: {answer.weight}

Yêu cầu:
Trả về DUY NHẤT JSON (không markdown):
{{"score": <number>, "feedback": "<nhận xét ngắn gọn>"}}
"""

                try:
                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )

                    raw_text = response.text.strip()

                    # 🧹 Phòng model bọc markdown
                    if raw_text.startswith("```"):
                        raw_text = (
                            raw_text.replace("```json", "")
                            .replace("```", "")
                            .strip()
                        )

                    data = json.loads(raw_text)

                    q_score = float(data.get("score", 0.0))
                    q_score = max(0.0, min(q_score, float(answer.weight)))

                    q_feedback = str(data.get("feedback", "")).strip()

                    total_score += q_score
                    feedback_parts.append(
                        f"Câu {index}: {q_feedback} ({q_score}/{answer.weight}đ)"
                    )

                except Exception as e:
                    logger.exception(f"Lỗi chấm câu {answer.question_id}")
                    feedback_parts.append(
                        f"Câu {index}: ❌ Lỗi AI khi chấm ({e})"
                    )

                # ⏳ Né rate limit
                time.sleep(3)

            final_feedback = "\n".join(feedback_parts)

            return GradingResult(
                submission_id=request.submission_id,
                score=round(total_score, 2),  # giữ float cho chuẩn
                feedback=final_feedback,
            )

        except Exception as e:
            logger.exception(
                f"Lỗi hệ thống chấm bài {request.submission_id}"
            )
            return GradingResult(
                submission_id=request.submission_id,
                score=0.0,
                feedback="Lỗi hệ thống nghiêm trọng khi xử lý bài nộp.",
                error=str(e),
            )
