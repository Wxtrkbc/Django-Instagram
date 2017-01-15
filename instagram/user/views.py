# coding=utf-8

from rest_framework import viewsets

from django.contrib.auth import get_user_model


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    pass