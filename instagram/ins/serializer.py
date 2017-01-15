# -*- coding: utf-8 -*-

from rest_framework import serializers

from ins.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
