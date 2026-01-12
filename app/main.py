import logging
from app.transport.rabbitmq_worker import RabbitMQWorker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    print(">>>>>>>>>>RUNNING<<<<<<<<<<")
    worker = RabbitMQWorker()
    worker.start()