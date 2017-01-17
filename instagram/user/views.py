# coding=utf-8

from django.contrib.auth import get_user_model, authenticate, login
from rest_framework import viewsets, status
from rest_framework.decorators import list_route

from util.response import error_response, empty_response
from ins.serializer import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['post'])
    def login(self, request):
        data = request.data
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
        else:
            return error_response('Login fail', status=status.HTTP_401_UNAUTHORIZED)
        return empty_response()
