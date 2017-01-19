# coding=utf-8
import json

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from ins.models import Ins, Comment
from util import const

User = get_user_model()


class TestUser(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(name='jason', password='123456')
        user2 = User.objects.create_user(name='lj', password='123', avatar='x1.path')
        user3 = User.objects.create_user(name='tom', password='123', avatar='x2.path')
        user4 = User.objects.create_user(name='arc', password='123', avatar='x3.path')

        user1.followed.add(*[user2, user3, user4])
        user1.followers.add(user2)

        in1 = Ins.objects.create(user=user1, content='ins1.path')
        Ins.objects.create(user=user1, content='ins2.path')

        Comment.objects.create(user=user2, ins=in1, body='nice', type=const.INS_COMMENT)
        Comment.objects.create(user=user2, ins=in1)
        Comment.objects.create(user=user3, ins=in1)
        Comment.objects.create(user=user4, ins=in1)

    def test_register(self):
        url = reverse("user-list")
        data = {
            'name': 'kobe',
            'phone': '18600138888',
            'password': '123456',
        }

        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'kobe')
        user = User.objects.filter(name='kobe').first()
        self.assertEqual(user.check_password('123456'), True)

    def test_login(self):
        url = reverse("user-login")
        data = {
            'username': 'jason',
            'password': '123456'
        }

        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_followers(self):
        url = reverse("user-followers", args=['jason'])
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], 'lj')

    def test_following(self):
        url = reverse("user-following", args=['jason'])
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 3)

    def test_user_profile(self):
        user = User.objects.get(name='jason')
        url = reverse("user-detail", args=[user.name])
        response = self.client.get(url)
        self.assertEqual(response.json()['followers'], 1)

    def test_user_ins(self):
        url = reverse("user-ins", args=['jason'])
        response = self.client.get(url)
        self.assertEqual(response.json()['results'][0]['comments_count'], 1)
