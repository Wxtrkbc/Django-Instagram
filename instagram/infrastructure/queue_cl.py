# coding: utf-8

import json
import pika

from django.conf import settings


class QueueManager:

    def __init__(self, host=settings.QUEUE_HOST):
        self.host = host
        self.connection = None
        self.channel = None

    def publish_ins(self, data):
        self.channel.queue_declare(queue='publish_ins')  # declare queue name is publish_ins

        # routing_key ---> 指定为队列的名称
        self.channel.basic_publish(exchange='', routing_key='publish_ins', body=json.dumps(data))

    def __enter__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        return self.connection.close()
