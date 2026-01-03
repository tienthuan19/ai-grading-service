# test_sender.py
import pika
import json
from app.core.config import settings

# 1. Kết nối RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    )
)
channel = connection.channel()

# Đảm bảo queue tồn tại
channel.queue_declare(queue=settings.QUEUE_REQUEST, durable=True)

# 2. Tạo dữ liệu giả (Giả vờ là Backend gửi qua)
fake_submission = {
    "submission_id": "TEST_001",
    "question_content": "Giải thích ngắn gọn nguyên lý tảng băng trôi của Hemingway.",
    "model_answer": "Nguyên lý tảng băng trôi: Phần nổi là văn bản câu chữ, phần chìm là hàm ý sâu xa, cảm xúc người viết muốn truyền tải.",
    "student_answer": "Là viết ít nhưng hiểu nhiều. Giống như tảng băng chỉ nổi 1 phần, còn 7 phần chìm dưới nước.",
    "max_score": 10.0
}

# 3. Gửi tin nhắn vào Queue
channel.basic_publish(
    exchange='',
    routing_key=settings.QUEUE_REQUEST,
    body=json.dumps(fake_submission),
    properties=pika.BasicProperties(
        delivery_mode=2,  # Tin nhắn bền vững
    )
)

print(f" [x] Đã gửi bài tập mẫu lên queue: {settings.QUEUE_REQUEST}")
connection.close()