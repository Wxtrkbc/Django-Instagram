# -*- coding: utf-8 -*-

from rest_framework import serializers
from django.contrib.auth import get_user_model

from util.schema import optional_dict
from util import errors
from util.exception import INSException
from util.schema import get_object_or_400
from ins.models import Ins, Comment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    followed = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    location = serializers.JSONField(binary=True, required=False)

    class Meta:
        fields = (
            'uuid', 'name', 'email', 'phone', 'avatar', 'location', 'sex', 'brief', 'level',
            'password', 'followed', 'followers')
        model = User
        read_only_fields = ('followed', 'followers')

    def validate(self, attrs):
        allowed_keys = ['name', 'email', 'phone', 'password', 'avatar', 'location', 'sex']
        user_data = optional_dict(attrs, allowed_keys)
        if self._is_exist_user(user_data):
            raise INSException(code=errors.ERR_ALREADY_REGISTER, message="User already register")
        return attrs

    @staticmethod
    def _is_exist_user(data):
        if 'name' in data and User.objects.filter(name=data['name']):
            return True
        if 'phone' in data and User.objects.filter(phone=data['phone']):
            return True
        if 'email' in data and User.objects.filter(email=data['email']):
            return True
        return False

    def save(self, **kwargs):
        User.objects.create_user(**self.validated_data)

    def get_followed(self, obj):
        return obj.followed.count() if isinstance(obj, User) and obj.followed else 0

    def get_followers(self, obj):
        return obj.followers.count() if isinstance(obj, User) and obj.followers else 0


class CommentSerializer(serializers.ModelSerializer):

    # user = serializers.CharField(source="user.name")
    user = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'user', 'type', 'body', 'created_at')
        model = Comment

    def get_user(self, obj):
        return _get_user_profile(obj)


class InsSerializer(serializers.ModelSerializer):

    # user = serializers.CharField(source="user.name")
    # comments = CommentSerializer(many=True)
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('uuid', 'user', 'desc', 'content', 'likes_count', 'comments_count')
        model = Ins

    def get_user(self, obj):
        return _get_user_profile(obj)

    def get_likes_count(self, obj):
        return Ins.ins_objects.get_likes_count(obj) if isinstance(obj, Ins) else 0

    def get_comments_count(self, obj):
        return Ins.ins_objects.get_comments_count(obj) if isinstance(obj, Ins) else 0


def _get_user_profile(obj):
    # 获取评论者的用户信息或者用户发表ins时候的用户信息
    user = get_object_or_400(User, uuid=obj['user']) if isinstance(obj, dict) else obj.user
    return {
        'avatar': user.avatar,
        'username': user.name,
        'uuid': user.uuid
    }
