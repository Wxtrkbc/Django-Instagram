# coding: utf-8

import json
# import django
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "instagram.settings")
# django.setup()

from django.shortcuts import get_object_or_404
from infrastructure.queue_cl import QueueManager
from infrastructure.redis_cl import Redis
from ins.models import Ins, User
from ins.serializer import InsSerializer


class INSDispatcher:
    """
    - 接受队列里所有的ins
    - 存入数据库
    - 检查这条ins要发给哪些人（关注该ins的粉丝）并且该粉丝最近一天有登录过（活跃用户）
    - 将此ins发送到活跃粉丝用户的队列里
    """

    def __init__(self):
        self.redis = Redis.get_redis()
        self.queue_manager = QueueManager()

    def save_ins(self, data):
        data['user'] = get_object_or_404(User, name=data.pop('user'))
        ins = Ins.objects.create(**data)
        return data['user'], InsSerializer(ins).data

    def push_followers(self, user, ins_info):
        followers = user.followers.all()
        ins_info['uuid'] = str(ins_info['uuid'])
        for people in followers:
            queue_name = 'uid_{}'.format(people.uuid)
            if self.redis.get('active_user_{}'.format(people.uuid)):
                self.queue_manager.channel.queue_declare(queue=queue_name, durable=True)
                self.queue_manager.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(ins_info)
                )

    def callback(self, ch, method, properties, body):
        data = json.loads(str(body, encoding='utf-8'))
        user, ins_data = self.save_ins(data)
        self.push_followers(user, ins_data)

    def listen_ins(self):
        self.queue_manager.channel.queue_declare(queue='ins_publish', durable=True)
        self.queue_manager.channel.basic_qos(prefetch_count=1)
        self.queue_manager.channel.basic_consume(self.callback, queue='ins_publish', no_ack=False)
        self.queue_manager.channel.start_consuming()


ins_dispatcher = INSDispatcher()
ins_dispatcher.listen_ins()

"""
 - durable  需要和前面发布消息保持消息持久化一起来使用
    - True  声明队列为持久化
    - False

 - no_ack
    - True  当消息被 RabbitMQ发送给消费者（consumers）之后，马上就会在内存中移除，消息可能丢失
    - False 如果消费者（consumer）挂掉了，没有发送响应，RabbitMQ 就会认为消息没有被完全处理，
      然后重新发送给其他消费者（consumer）

 - 公平调度
    - 轮询（round-robin）RabbitMQ 会按顺序得把消息发送给每个消费者（consumer）。
      平均每个消费者都会收到同等数量得消息。（默认）

    - 使用 basic.qos 方法，并设置 prefetch_count=1
      告诉RabbitMQ，再同一时刻，不要发送超过1条消息给一个工作者（worker），
      直到它已经处理了上一条消息并且作出了响应


## 交换机

    - 扇型交换机（fanout）
    ```
    channel.exchange_declare(exchange='logs', type='fanout')

    channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)

    ```

    # 手动创建一个随机的队列名
    result = channel.queue_declare()
    通过result.method.queue 获得已经生成的随机队列名

    # 与消费者（consumer）断开连接的时候，这个队列应当被立即删除
    result = channel.queue_declare(exclusive=True)

    交换器和队列之间的联系我们称之为绑定（binding）
    channel.queue_bind(exchange='logs', queue=result.method.queue)

    - 路由
        - 绑定键（binding key）
          绑定键的意义取决于交换机（exchange）的类型,扇型交换机会忽略这个值。
        ```
        channel.queue_bind(exchange=exchange_name,
                   queue=queue_name,
                   routing_key='black')
        ```
    - 直接交换机
     channel.exchange_declare(exchange='direct_logs', type='direct')

     channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)

    - 主题交换机

    主题交换机可以表现出跟其他交换机类似的行为

    当一个队列的绑定键为 "#"的时候，这个队列将会无视消息的路由键，接收所有的消息。

    当 * 和 # 这两个特殊字符都未在绑定键中出现的时候，此时主题交换机就拥有的直连交换机的行为。



"""
