from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from ins.models import Ins
from ins.serializer import InsSerializer, CommentSerializer
from util.schema import get_object_or_400, check_keys
from util.response import json_response, empty_response
from util.exception import INSException
from util import errors
from app.func import format_ins_detail


class InsViewSet(viewsets.ModelViewSet):
    queryset = Ins.objects.all()
    serializer_class = InsSerializer
    lookup_value_regex = '[0-9a-f-]{36}'

    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    @detail_route(methods=['get'])
    def detail(self, request, pk):
        ins = get_object_or_400(Ins, uuid=pk)
        ins_detail = format_ins_detail(ins)
        return json_response(ins_detail)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        ins = get_object_or_400(Ins, uuid=pk)
        comments = Ins.ins_objects.get_comments(ins)
        page = self.paginate_queryset(CommentSerializer(comments, many=True).data)
        if page is not None:
            return self.get_paginated_response(page)
        return json_response(page)

    @transaction.atomic
    def create_ins(self, request):
        data = request.data
        ins_keys = ['desc', 'content', 'type']
        check_keys(data, ins_keys)
        data.update({'user': request.user})
        ins = Ins.objects.create(**data)
        return json_response(InsSerializer(ins).data)

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
