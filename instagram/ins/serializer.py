# -*- coding: utf-8 -*-

from rest_framework import serializers
from django.contrib.auth import get_user_model

from util.schema import optional_dict
from util import errors
from util.exception import INSException

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    followed = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'uuid', 'name', 'email', 'phone', 'avatar', 'location', 'sex', 'brief', 'level',
            'password', 'followed', 'followers', 'ins')
        model = User
        read_only_fields = ('followed', 'followers', 'ins')

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
        return obj.followed.count() if obj.followed else 0

    def get_followers(self, obj):
        return obj.followers.count() if obj.followers else 0
