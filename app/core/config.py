from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Grading Service"

    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    AI_SUBMISSION_QUEUE: str = "ai_submission_queue"
    AI_RESULT_QUEUE: str = "ai_results_queue"
    AI_EXCHANGE: str = "ai.exchange"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()