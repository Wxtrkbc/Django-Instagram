# -*- coding: utf-8 -*-

from rest_framework import serializers

from ins.models import User
from util.schema import validate_value, optional_dict
from util import const
from util import errors
from util.exception import INSException


class UserSerializer(serializers.ModelSerializer):
    # avatar = serializers.CharField(required=False)

    class Meta:
        fields = ('uuid', 'name', 'email', 'phone', 'avatar', 'location', 'sex', 'brief', 'level')
        model = User

    def validate_sex(self, value):
        validate_value(value, const.SEX_TYPES)
        return value

    def validate(self, attrs):
        user_keys = ['name', 'email', 'phone', 'password', 'avatar', 'location', 'sex']
        user_data = optional_dict(attrs, user_keys)
        if self._is_exist_user(user_data):
            raise INSException(code=errors.ERR_ALREADY_REGISTER, message="User already register")
        return attrs

    def _is_exist_user(self, data):
        user = None
        if 'phone' in data:
            user = User.objects.filter(phone=data['phone'])
        if 'email' in data:
            user = User.objects.filter(email=data['email'])
        return True if user else False
