# coding=utf-8
import json

from django.urls import reverse
from django.test import TestCase


class TestUser(TestCase):
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
