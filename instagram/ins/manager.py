# coding: utf-8

from django.db import models
from django.contrib.auth.models import UserManager
from django.conf import settings

from util import const


class INSUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, password, email, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, email=None, **extra_fields):
        return self._create_user(password, email, **extra_fields)

    def get_followers(self, user):
        return user.followers.values('name', 'avatar').order_by('-created_at')

    def get_following(self, user):
        return user.followed.values('name', 'avatar').order_by('-created_at')

    def get_ins(self, user):
        return user.ins.all().order_by('-created_at')


class InsManager(models.Manager):
    def get_comments_count(self, ins):
        return ins.comments.filter(type=const.INS_COMMENT).count()

    def get_likes_count(self, ins):
        return ins.comments.filter(type=const.INS_LIKE).count()

    def get_last_comments(self, ins):
        return ins.comments.filter(type=const.INS_COMMENT).values('user', 'body', 'id',
                                                                  'created_at').order_by(
            '-created_at')[0:settings.LATEST_COMMENTS_NUM]

    def get_comments(self, ins):
        return ins.comments.filter(type=const.INS_COMMENT).values('user', 'body', 'id',
                                                                  'created_at').order_by(
            '-created_at')
