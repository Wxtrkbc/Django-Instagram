from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from ins.models import Ins, Comment
from util import const

User = get_user_model()


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

    def test_ins_detail(self):
        in1 = Ins.objects.filter(content='ins1.path').first()
        url = reverse('ins-detail', args=[in1.uuid])
        # url = reverse('ins-get_ins_info', args=[in1.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ins_comment(self):
        in1 = Ins.objects.filter(content='ins1.path').first()
        url = reverse('ins-comments', args=[in1.uuid])
        response = self.client.get(url)
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
