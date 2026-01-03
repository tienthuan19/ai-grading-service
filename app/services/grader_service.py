import json
import logging
import time
import random
from google.genai import Client, types, errors

from app.core.config import settings
# 👇 Nhớ import GradingDetail
from app.models.schemas import GradingRequest, GradingResult, GradingDetail

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
  ...
]

Lưu ý: 
- Điểm số ("score") không được vượt quá "Điểm tối đa" của câu đó.
- Nếu học sinh không làm bài hoặc làm sai hoàn toàn, điểm là 0.
"""

        # 2. Gọi AI (Sử dụng cơ chế Retry)
        model_id = settings.GEMINI_MODEL
        response_text = ""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                response_text = response.text.strip()
                break

            except errors.ClientError as e:
                if e.code == 429:
                    wait_time = (10 * (attempt + 1)) + random.uniform(1, 5)
                    logger.warning(f"⚠️ Quá tải (429). Chờ {wait_time:.1f}s...")
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
                feedback="Lỗi: Không thể kết nối đến AI.",
                details=[]
            )

        # 3. Xử lý kết quả trả về
        total_score = 0.0
        feedback_lines = []
        details_list = [] # 👇 Danh sách chi tiết để gửi về Java

        try:
            if response_text.startswith("```"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            grading_data = json.loads(response_text)
            result_map = {item.get("question_id"): item for item in grading_data}

            for idx, answer in enumerate(request.essay_answers, start=1):
                res = result_map.get(answer.question_id, {})

                # Lấy điểm và feedback
                s = float(res.get("score", 0.0))
                s = max(0.0, min(s, float(answer.weight))) # Kẹp điểm
                f = res.get("feedback", "Không có nhận xét")

                # Cộng tổng
                total_score += s
                feedback_lines.append(f"Câu {idx}: {f} ({s}/{answer.weight}đ)")

                # 👇 THÊM VÀO DANH SÁCH CHI TIẾT
                details_list.append(GradingDetail(
                    question_id=answer.question_id,
                    score=s,
                    feedback=f
                ))

        except Exception as e:
            logger.exception("Lỗi khi xử lý JSON từ AI")
            return GradingResult(
                submission_id=request.submission_id,
                score=0.0,
                feedback="Lỗi xử lý nội bộ.",
                error=str(e),
                details=[]
            )

        # 4. Trả kết quả cuối cùng
        final_feedback = "\n".join(feedback_lines)
        logger.info(f"✅ Đã chấm xong bài {request.submission_id}. Tổng: {total_score}")

        return GradingResult(
            submission_id=request.submission_id,
            score=round(total_score, 2),
            feedback=final_feedback,
            details=details_list # 👈 Quan trọng: Gửi kèm danh sách chi tiết
        )