import pika
import json
import logging
import time
from app.core.config import settings
from app.models.schemas import GradingRequest
from app.services.grader_service import GraderService

logger = logging.getLogger(__name__)

class RabbitMQWorker:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        while True:
            try:
                creds = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
                params = pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=creds,
                    heartbeat=600
                )
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()

                self.channel.queue_declare(queue=settings.AI_SUBMISSION_QUEUE, durable=True)
                self.channel.queue_declare(queue=settings.AI_RESULT_QUEUE, durable=True)

                logger.info(f">>>>>>>>>>>>>CONNECT RabbitMQ! LISTENING>>>>>>>>>>>>: {settings.AI_SUBMISSION_QUEUE}")
                return
            except pika.exceptions.AMQPConnectionError:
                logger.warning("⚠️ Chưa thấy RabbitMQ, thử lại sau 5s...")
                time.sleep(5)

    def on_request(self, ch, method, props, body):
        try:
            payload = json.loads(body)
            logger.info(f"📩 Nhận bài ID: {payload.get('submission_id')}")
            request = GradingRequest(**payload)

            result = GraderService.grade_submission(request)

            ch.basic_publish(
                exchange='',
                routing_key=settings.AI_RESULT_QUEUE,
                body=json.dumps(result.model_dump(by_alias=True), ensure_ascii=False),

                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    priority=0
                )
            )
            logger.info(f"📤 Đã trả điểm ID: {result.submission_id}")

        except Exception as e:
            logger.error(f"❌ Lỗi xử lý: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.connect()
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(queue=settings.AI_SUBMISSION_QUEUE, on_message_callback=self.on_request)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()