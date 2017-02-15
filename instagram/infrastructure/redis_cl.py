# coding=utf-8

import redis

from django.conf import settings


class Redis:

    __instance = None

    def __init__(self, redis_setting=settings.REDIS_CONNECT_DICT):
        self.pool = redis.ConnectionPool(**redis_setting)
        self.redis = redis.Redis(connection_pool=self.pool)

    @staticmethod
    def get_redis():
        if not Redis.__instance:
            Redis.__instance = Redis()
        return Redis.__instance.redis


# class Singleton:
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, '__instance'):
#             cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
#         return cls.__instance
