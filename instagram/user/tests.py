# coding=utf-8
import json

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUser(TestCase):
    def setUp(self):
        User.objects.create_user(name='jason', password='123456')

    def test_register(self):
        url = reverse("user-list")
        data = {
            'name': 'Jason',
            'phone': '18600138888',
            'password': '123456',
        }

        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Jason')
        user = User.objects.filter(name='Jason').first()
        self.assertEqual(user.check_password('123456'), True)

    def test_login(self):
        url = reverse("user-login")
        data = {
            'username': 'jason',
            'password': '123456'
        }

        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 204)
