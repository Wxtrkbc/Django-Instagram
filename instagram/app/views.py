# coding: utf-8

import hashlib
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from django.conf import settings

import requests
from rest_framework import viewsets, filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

from app.func import format_ins_detail
from ins.forms import InsFilter
from ins.models import Ins, Comment
from ins.serializer import InsSerializer, CommentSerializer
from util import errors, const
from util.exception import INSException
from util.response import json_response, empty_response
from util.schema import get_object_or_400, check_keys, validate_value
from infrastructure.queue_cl import QueueManager


User = get_user_model()


class UpdateHookMixin(object):
    """Mixin class to send update information to the websocket server."""

    def _build_hook_url(self, obj):
        model_name = 'user' if isinstance(obj, User) else obj.__class__.__name__.lower()
        return "{}://{}/{}/{}".format(
            'https' if settings.WEBSOCKET_SECURE else 'http',
            settings.WEBSOCKET_SERVER, model_name, obj.pk
        )

    def _send_hook_request(self, obj, method):
        url = self._build_hook_url(obj)
        if method in ('POST', 'PUT', 'PATCH'):
            serializer = self.get_serializer(obj)
            render = JSONRenderer()
            context = {'request': self.request}
            body = render.render(serializer.data, renderer_context=context)
        else:
            body = None

        headers = {
            'content-type': 'application/json',
            'X-Signature': self._build_hook_signature(method, url, body)
        }
        try:
            response = requests.request(method, url, data=body, timeout=0.5, headers=headers)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.RequestException:
            # 4xx or 5xx
            pass

    def _build_hook_signature(self, method, url, body):
        signer = TimestampSigner(settings.WEBSOCKET_SECRET)
        value = '{method}:{url}:{body}'.format(
            method=method.lower(),
            url=url,
            body=hashlib.sha256(body or b'').hexdigest()
        )
        return signer.sign(value)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._send_hook_request(serializer.instance, 'POST')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._send_hook_request(serializer.instance, 'PUT')

    def perform_destroy(self, instance):
        self._send_hook_request(instance, 'DELETE')
        super().perform_destroy(instance)


class InsViewSet(UpdateHookMixin, viewsets.ModelViewSet):
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

        # data.update({'user': request.user})
        # ins = Ins.objects.create(**data)
        # return json_response(InsSerializer(ins).data)
        # with QueueManager() as queue_manager:
        #     queue_manager.publish_ins(data=data)

        queue_manager = QueueManager()
        queue_manager.publish_ins(data=data)
        queue_manager.close()
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
