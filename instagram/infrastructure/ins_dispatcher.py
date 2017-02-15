# coding: utf-8

from django.shortcuts import get_object_or_404

from infrastructure.queue_cl import QueueManager
from infrastructure.redis_cl import Redis
from ins.models import Ins, User


class INSDispatcher:

    """
    - 接受队列里所有的ins
    - 存入数据库
    - 检查这条ins要发给哪些人（关注该ins的粉丝）并且该粉丝最近一天有登录过（活跃用户）
    - 将此ins发送到活跃粉丝用户的队列里
    """

    def __init__(self):
        self.redis = Redis.get_redis()

    def save_ins(self, data):
        data['user'] = get_object_or_404(User, name=data.pop('user'))
        return Ins.objects.create(**data)

    def push_followers(self):
        pass

    def listen_ins(self):
        pass
