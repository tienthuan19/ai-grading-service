import logging
from app.transport.rabbitmq_worker import RabbitMQWorker

# Cấu hình log ra màn hình
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    print("🚀 AI Grading Service đang khởi động...")
    worker = RabbitMQWorker()
    worker.start()