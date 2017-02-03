from rest_framework import viewsets
from rest_framework.decorators import detail_route

from ins.models import Ins
from ins.serializer import InsSerializer
from ins.permission import IsOwnerOrReadOnly
from util.schema import get_object_or_400
from util.response import json_response
from app.func import format_ins_detail


class InsViewSet(viewsets.ModelViewSet):
    queryset = Ins.objects.all()
    serializer_class = InsSerializer
    lookup_value_regex = '[0-9a-f-]{36}'
    permission_classes = (IsOwnerOrReadOnly,)

    @detail_route(methods=['get'])
    def detail(self, request, pk):
        ins = get_object_or_400(Ins, uuid=pk)
        ins_detail = format_ins_detail(ins)
        return json_response(ins_detail)
