# coding: utf-8

import json
import pika

from django.conf import settings


class QueueManager:
    def __init__(self, host=settings.QUEUE_HOST):
        self.host = host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

    def publish_ins(self, data):
        self.channel.queue_declare(queue='ins_publish',
                                   durable=True)  # declare queue name is publish_ins

        # routing_key ---> queue name
        self.channel.basic_publish(
            exchange='',  # 默认或者匿名交换机，消息将会根据指定的 routing_key 分发到指定的队列
            routing_key='publish_ins',
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,                # make message persistent
            )
        )

    def close(self):
        return self.connection.close()

    # def __enter__(self):
    #     self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
    #     self.channel = self.connection.channel()
    #     return self
    #
    # def __exit__(self, exc_ty, exc_val, tb):
    #     return self.connection.close()
