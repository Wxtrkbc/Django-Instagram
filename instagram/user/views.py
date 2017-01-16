# coding=utf-8
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import list_route

from util.schema import optional_dict, validate_value
from util import const
from util import errors
from util.exception import INSException
from util.response import json_response
from ins.serializer import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['post'])
    def register(self, request):
        """
        注册这里没有采用任何安全措施，本项目的重点不在这里
        这里只考虑最简单的情况,
        """
        user_keys = ['name', 'email', 'phone', 'password', 'avatar', 'location', 'sex']
        user_data = optional_dict(request.data, user_keys)
        if 'sex' in user_data:
            validate_value(user_data['sex'], const.SEX_TYPES)

        if _is_exist_user(user_data):
            raise INSException(code=errors.ERR_ALREADY_REGISTER, message="User already register")
        user = User.objects.create(**user_data)

        return json_response(UserSerializer(user).data)


def _is_exist_user(data):
    user = None
    if 'phone' in data:
        user = User.objects.filter(phone=data['phone'])
    if 'email' in data:
        user = User.objects.filter(email=data['email'])
    return True if user else False
