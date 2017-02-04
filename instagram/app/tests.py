import json
import functools

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from ins.models import Ins, Comment
from util import const

User = get_user_model()


def test_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        user = User.objects.first()
        self.client.force_login(user)
        return func(*args, **kwargs)
    return wrapper


class TestIns(TestCase):
    def setUp(self):
        # init user
        user1 = User.objects.create_user(name='jason', password='123456')
        user2 = User.objects.create_user(name='lj', password='123', avatar='x1.path')
        user3 = User.objects.create_user(name='tom', password='123', avatar='x2.path')
        user4 = User.objects.create_user(name='arc', password='123', avatar='x3.path')
        user1.followed.add(*[user2, user3, user4])
        user1.followers.add(user2)

        # init ins
        in1 = Ins.objects.create(user=user1, content='ins1.path')
        Ins.objects.create(user=user1, content='ins2.path')

        # init comment
        Comment.objects.create(user=user2, ins=in1, body='nice', type=const.INS_COMMENT)
        Comment.objects.create(user=user2, ins=in1)
        Comment.objects.create(user=user3, ins=in1)
        Comment.objects.create(user=user4, ins=in1)

    @test_login
    def test_ins_detail(self):
        in1 = Ins.objects.filter(content='ins1.path').first()
        url = reverse('ins-detail', args=[in1.uuid])
        # url = reverse('ins-get_ins_info', args=[in1.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @test_login
    def test_ins_comment(self):
        in1 = Ins.objects.filter(content='ins1.path').first()
        url = reverse('ins-comments', args=[in1.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    @test_login
    def test_create_ins(self):

        data = json.dumps({
            'desc': 'in1',
            'content': 'in1.path'
        })

        url = reverse('create-ins')

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.json()['desc'], 'in1')
