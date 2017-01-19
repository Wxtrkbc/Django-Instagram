
from ins.models import Ins


def format_ins(queryset):
    def _each(ins):
        temp = {
            'content': ins.content,
            'likes_count': Ins.ins_objects.get_likes_count(ins),
            'comments_count': Ins.ins_objects.get_comments_count(ins)
        }
        return temp
    return [_each(x) for x in queryset]
