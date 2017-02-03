
from ins.models import Ins
from ins.serializer import CommentSerializer, InsSerializer


def format_ins_detail(ins):
    ins_detail = InsSerializer(ins).data
    last_comments = Ins.ins_objects.get_last_comments(ins)

    ins_detail['last_comments'] = CommentSerializer(last_comments, many=True).data
    return ins_detail
