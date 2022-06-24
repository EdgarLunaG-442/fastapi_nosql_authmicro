import pika
import os
from config import DEFAULT_SETTINGS

PUBLISH_QUEUE = os.getenv('PUBLISH_QUEUE', DEFAULT_SETTINGS.get('PUBLISH_QUEUE'))
PUBLISH_EXCHANGE = os.getenv('PUBLISH_EXCHANGE', DEFAULT_SETTINGS.get('PUBLISH_EXCHANGE'))
RABBIT_HOST = os.getenv('RABBIT_HOST', DEFAULT_SETTINGS.get('RABBIT_HOST'))
RABBIT_VHOST = os.getenv('RABBIT_VHOST', DEFAULT_SETTINGS.get('RABBIT_VHOST'))
RABBIT_USER = os.getenv('RABBIT_USER', DEFAULT_SETTINGS.get('RABBIT_USER'))
RABBIT_PASS = os.getenv('RABBIT_PASS', DEFAULT_SETTINGS.get('RABBIT_PASS'))

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)


class PikaClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, 5672, RABBIT_VHOST, credentials))
        self.channel = self.connection.channel()
        self.publish_queue = self.channel.queue_declare(queue=PUBLISH_QUEUE, durable=False)
        self.publish_exchange = self.channel.exchange_declare(exchange=PUBLISH_EXCHANGE, durable=True)
        self.publish_bind = self.channel.queue_bind(PUBLISH_QUEUE, PUBLISH_EXCHANGE)

    def reload_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, 5672, RABBIT_VHOST, credentials))
        self.channel = self.connection.channel()


pika_client: PikaClient = PikaClient()