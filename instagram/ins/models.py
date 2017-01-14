# coding: utf-8

import uuid
import jsonfield

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager

from util import const


class Time(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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


class User(AbstractBaseUser, Time):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, blank=True, default='')
    email = models.CharField(max_length=256, db_index=True, blank=True, default='')
    phone = models.CharField(max_length=16, db_index=True, blank=True, default='')
    avatar = models.CharField(max_length=256)
    location = jsonfield.JSONField(blank=True, default={})
    sex = models.CharField(max_length=12, choices=const.SEX_TYPE, default=const.SEX_UNDEFINED)
    brief = models.CharField(max_length=512, blank=True, default='')
    followed = models.ManyToManyField('self', null=True, related_name='followers',
                                      symmetrical=False)

    USERNAME_FIELD = 'uuid'
    REQUIRED_FIELDS = []

    object = INSUserManager()

    def __str__(self):
        return '{} {}'.format(self.name, self.phone)


class Ins(Time):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    desc = models.CharField(max_length=1024, blank=True, default='')
    type = models.CharField(max_length=12, choices=const.INS_CONTENT_TYPE,
                            default=const.INS_CONTENT_PICTURE)
    content = models.CharField(max_length=128)
    comments = models.ForeignKey('Comment', null=True)

    def __str__(self):
        return self.desc


class Comment(models.Model):
    user = models.ForeignKey(User)
    ins = models.ForeignKey(Ins)
    type = models.CharField(max_length=12, choices=const.COMMENT_TYPE, default=const.INS_LIKE)
    body = models.CharField(max_length=256, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
