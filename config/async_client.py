import pika
import os

ACTIVATION_QUEUE = os.getenv('ACTIVATION_QUEUE')
PASSWORD_RECOVERY_QUEUE = os.getenv('PASSWORD_RECOVERY_QUEUE')
PUBLISH_EXCHANGE = os.getenv('PUBLISH_EXCHANGE')
RABBIT_HOST = os.getenv('RABBIT_HOST')
RABBIT_PORT = os.getenv('RABBIT_PORT')
RABBIT_USER = os.getenv('RABBIT_USER')
RABBIT_PASS = os.getenv('RABBIT_PASS')

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)


class PikaClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, port=int(RABBIT_PORT), credentials=credentials))
        self.channel = self.connection.channel()
        self.publish_exchange = self.channel.exchange_declare(exchange=PUBLISH_EXCHANGE, durable=True)
        self.activation_queue = self.channel.queue_declare(queue=ACTIVATION_QUEUE, durable=False)
        self.password_recovery_queue = self.channel.queue_declare(queue=PASSWORD_RECOVERY_QUEUE, durable=False)
        self.activation_bind = self.channel.queue_bind(ACTIVATION_QUEUE, PUBLISH_EXCHANGE)
        self.password_recovery_bind = self.channel.queue_bind(PASSWORD_RECOVERY_QUEUE, PUBLISH_EXCHANGE)

    def reload_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, port=int(RABBIT_PORT), credentials=credentials))
        self.channel = self.connection.channel()


pika_client: PikaClient = PikaClient()
