# coding: utf-8

from django.db import transaction
from rest_framework import viewsets, filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from app.func import format_ins_detail
from ins.forms import InsFilter
from ins.models import Ins, Comment
from ins.serializer import InsSerializer, CommentSerializer
from util import errors, const
from util.exception import INSException
from util.response import json_response, empty_response
from util.schema import get_object_or_400, check_keys, validate_value
from infrastructure.queue_cl import QueueManager


class InsViewSet(viewsets.ModelViewSet):
    queryset = Ins.objects.all()
    serializer_class = InsSerializer
    lookup_value_regex = '[0-9a-f-]{36}'

    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    filter_backends = (
        filters.DjangoFilterBackend,
    )
    filter_class = InsFilter

    @detail_route(methods=['get'])
    def detail(self, request, pk):
        ins = get_object_or_400(Ins, uuid=pk)
        ins_detail = format_ins_detail(ins)
        return json_response(ins_detail)

    @transaction.atomic
    @detail_route(methods=['get', 'post'])
    def comments(self, request, pk):
        # globals()['_comments_{}'.format(request.method.lower())](self, request, pk)
        ins = get_object_or_400(Ins, uuid=pk)
        if request.method == 'GET':
            comments = Ins.ins_objects.get_comments(ins)
            page = self.paginate_queryset(CommentSerializer(comments, many=True).data)
            if page is not None:
                return self.get_paginated_response(page)
            return json_response(page)
        else:
            data = request.data
            comment_keys = ['type', 'body']
            check_keys(data, comment_keys)
            if 'type' in data:
                validate_value(data['type'], const.COMMENT_TYPES)
            data.update({'user': request.user, 'ins': ins})
            comment = Comment.objects.create(**data)
            return json_response(CommentSerializer(comment).data)

    @transaction.atomic
    def create_ins(self, request):
        data = request.data
        ins_keys = ['desc', 'content', 'type']
        check_keys(data, ins_keys)
        data.update({'user': request.user.name})

        # 这里直接将数据放回给前端，然后将ins数据发送到队列中去
        # data.update({'user': request.user})
        # ins = Ins.objects.create(**data)
        # return json_response(InsSerializer(ins).data)
        with QueueManager() as queue_manager:
            queue_manager.publish_ins(data=data)
        return json_response(data)

    @transaction.atomic
    def delete_ins(self, request, uuid):
        # ins = get_object_or_400(Ins, uuid=uuid)
        ins = Ins.objects.filter(uuid=uuid).first()
        if not ins:
            return empty_response()
        if ins.user != request.user:
            raise INSException(code=errors.ERR_UNSUPPORTED, message='This INS is not for you')
        ins.delete()
        return empty_response()
