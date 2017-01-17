# -*- coding: utf-8 -*-

from rest_framework import serializers
from django.contrib.auth import get_user_model

from util.schema import optional_dict
from util import errors
from util.exception import INSException

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('uuid', 'name', 'email', 'phone', 'avatar', 'location', 'sex', 'brief', 'level')
        model = User

    def validate(self, attrs):
        user_keys = ['name', 'email', 'phone', 'password', 'avatar', 'location', 'sex']
        user_data = optional_dict(attrs, user_keys)
        if self._is_exist_user(user_data):
            raise INSException(code=errors.ERR_ALREADY_REGISTER, message="User already register")
        return attrs

    @staticmethod
    def _is_exist_user(data):
        user = None
        if 'phone' in data:
            user = User.objects.filter(phone=data['phone'])
        if 'email' in data:
            user = User.objects.filter(email=data['email'])
        return True if user else False

    def save(self, **kwargs):
        User.objects.create_user(**self.validated_data)
