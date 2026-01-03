import json
import logging
import time
import random
from google.genai import Client, types, errors

from app.core.config import settings
from app.models.schemas import GradingRequest, GradingResult

logger = logging.getLogger(__name__)

# Khởi tạo Client
client = Client(api_key=settings.GOOGLE_API_KEY)

class GraderService:
    @staticmethod
    def grade_submission(request: GradingRequest) -> GradingResult:
        """
        Chiến thuật: GOM TẤT CẢ CÂU HỎI VÀO 1 PROMPT (BATCH PROCESSING)
        """

        # 1. Chuẩn bị nội dung Prompt
        # Chúng ta sẽ xây dựng một chuỗi văn bản chứa toàn bộ đề bài và bài làm
        questions_content = ""
        for idx, answer in enumerate(request.essay_answers, start=1):
            questions_content += f"""
---
Câu hỏi {idx} (ID: {answer.question_id}):
- Đề bài: {answer.question_text}
- Đáp án mẫu: {answer.model_answer or "Không có, chấm theo kiến thức chuẩn."}
- Bài làm học sinh: {answer.student_answer}
- Điểm tối đa: {answer.weight}
"""

        # Prompt tổng hợp
        final_prompt = f"""
Bạn là một giáo viên chấm thi công tâm và chính xác.
Dưới đây là danh sách các câu hỏi và bài làm của một học sinh. 
Hãy chấm điểm từng câu dựa trên đáp án mẫu và thang điểm.

DANH SÁCH CÂU HỎI:
{questions_content}

---
YÊU CẦU ĐẦU RA (OUTPUT FORMAT):
Trả về DUY NHẤT một chuỗi JSON (JSON Array) chứa kết quả chấm cho tất cả các câu. 
Không dùng markdown block (```json). Cấu trúc như sau:

[
  {{
    "question_id": "ID của câu hỏi (copy chính xác từ đề)",
    "score": <số điểm chấm được (float)>,
    "feedback": "<nhận xét ngắn gọn, súc tích>"
  }},
  ... (tiếp tục cho các câu còn lại)
]

Lưu ý: 
- Điểm số ("score") không được vượt quá "Điểm tối đa" của câu đó.
- Nếu học sinh không làm bài hoặc làm sai hoàn toàn, điểm là 0.
"""

        # 2. Gọi AI (Sử dụng cơ chế Retry để chống crash)
        model_id = settings.GEMINI_MODEL
        response_text = ""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json" # Bắt buộc AI trả về JSON
                    ),
                )
                response_text = response.text.strip()
                break # Thành công thì thoát vòng lặp

            except errors.ClientError as e:
                if e.code == 429: # Lỗi Rate Limit
                    wait_time = (10 * (attempt + 1)) + random.uniform(1, 5)
                    logger.warning(f"⚠️ Quá tải (429). Chờ {wait_time:.1f}s thử lại ({attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Lỗi API khác: {e}")
                    raise e
            except Exception as e:
                logger.error(f"❌ Lỗi không xác định: {e}")
                time.sleep(5)

        if not response_text:
            return GradingResult(
                submission_id=request.submission_id,
                score=0.0,
                feedback="Lỗi: Không thể kết nối đến AI sau nhiều lần thử.",
                error="AI Response Empty"
            )

        # 3. Xử lý kết quả trả về (Parsing JSON)
        total_score = 0.0
        feedback_lines = []

        try:
            # Clean markdown nếu có
            if response_text.startswith("```"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Parse JSON Array
            grading_data = json.loads(response_text)

            # Duyệt qua từng kết quả để tính tổng
            # Tạo map để dễ tra cứu theo ID (phòng trường hợp AI trả về lộn xộn)
            result_map = {item.get("question_id"): item for item in grading_data}

            for idx, answer in enumerate(request.essay_answers, start=1):
                res = result_map.get(answer.question_id, {})

                # Lấy điểm (mặc định 0 nếu lỗi)
                s = float(res.get("score", 0.0))
                # Kẹp điểm trong khoảng [0, max_weight]
                s = max(0.0, min(s, float(answer.weight)))

                f = res.get("feedback", "Không có nhận xét")

                total_score += s
                feedback_lines.append(f"Câu {idx}: {f} ({s}/{answer.weight}đ)")

        except json.JSONDecodeError:
            logger.error(f"❌ AI trả về JSON lỗi: {response_text}")
            return GradingResult(
                submission_id=request.submission_id,
                score=0.0,
                feedback="Lỗi hệ thống: AI trả về định dạng không hợp lệ.",
                error="JSON Decode Error"
            )
        except Exception as e:
            logger.exception("Lỗi khi xử lý kết quả chấm thi")
            return GradingResult(
                submission_id=request.submission_id,
                score=0.0,
                feedback="Lỗi xử lý nội bộ.",
                error=str(e)
            )

        # 4. Trả kết quả cuối cùng
        final_feedback = "\n".join(feedback_lines)
        logger.info(f"✅ Đã chấm xong bài {request.submission_id}. Tổng điểm: {total_score}")

        return GradingResult(
            submission_id=request.submission_id,
            score=round(total_score, 2),
            feedback=final_feedback
        )