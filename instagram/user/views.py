# coding=utf-8

from django.contrib.auth import get_user_model, authenticate, login
from django.conf import settings
from rest_framework import viewsets, status, filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated

from ins.forms import UserFilter
from ins.serializer import UserSerializer
from user.func import format_ins
from util.response import error_response, empty_response, json_response
from util.schema import get_object_or_400, check_body_keys
from infrastructure.redis_cl import Redis
from infrastructure.queue_cl import QueueManager

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = User.USERNAME_FIELD
    authentication_classes = (SessionAuthentication,)

    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filter_class = UserFilter
    search_fields = ('name',)
    ordering_fields = ('created_at', 'name',)

    @list_route(methods=['post'])
    def login(self, request):
        data = request.data
        check_body_keys(data, ['username', 'password'])
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)

            # target user as active user
            redis = Redis.get_redis()
            redis.set('active_user_{}'.format(user.uuid), str(user.uuid),
                      ex=settings.USER_ACTIVE_EX)
        else:
            return error_response('Login fail', status=status.HTTP_401_UNAUTHORIZED)
        return empty_response()

    @detail_route(methods=['get'])
    def followers(self, request, name):
        user = get_object_or_400(User, name=name)
        followers = User.objects.get_followers(user)
        page = self.paginate_queryset(followers)
        if page is not None:
            return self.get_paginated_response(page)
        return json_response(page)

    @detail_route(methods=['get'])
    def following(self, request, name):
        user = get_object_or_400(User, name=name)
        following = User.objects.get_following(user)
        page = self.paginate_queryset(following)
        if page is not None:
            return self.get_paginated_response(page)
        return json_response(page)

    @detail_route(methods=['patch'], permission_classes=[IsAuthenticated])
    def follow(self, request, name):
        target_user = get_object_or_400(User, name=name)
        request.user.followed.add(target_user)
        return empty_response()

    @detail_route(methods=['patch'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, name):
        target_user = get_object_or_400(User, name=name)
        request.user.followed.remove(target_user)
        return empty_response()

    # 获取自己的ins和他人的ins
    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def ins(self, request, name):
        user = get_object_or_400(User, name=name)
        ins = User.objects.get_ins(user)
        page = self.paginate_queryset(format_ins(ins))
        if page is not None:
            return self.get_paginated_response(page)
        return json_response(page)

    # 个人主页展示自己关注用户的Ins（前提自己要活跃才能获取到相应的内容）
    # @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    @detail_route(methods=['get'])
    def followedins(self, request, name):
        user = get_object_or_400(User, name=name)
        queue_manager = QueueManager()
        queue_name = 'uid_{}'.format(user.uuid)
        ins_list = queue_manager.get_user_followed_ins(queue_name)
        page = self.paginate_queryset(ins_list)
        if page is not None:
            return self.get_paginated_response(page)
        return json_response(page)
