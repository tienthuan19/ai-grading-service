from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Cấu hình Project
    PROJECT_NAME: str = "AI Grading Service"

    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    # Google Gemini (Bắt buộc phải khớp với .env)
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Queues (Bắt buộc phải khớp với .env)
    AI_SUBMISSION_QUEUE: str = "ai_submission_queue"
    AI_RESULT_QUEUE: str = "ai_results_queue"
    AI_EXCHANGE: str = "ai.exchange"

    class Config:
        env_file = ".env"
        extra = "ignore" # Bỏ qua các biến thừa khác trong .env nếu có

# --- DÒNG QUAN TRỌNG BỊ THIẾU ---
settings = Settings()