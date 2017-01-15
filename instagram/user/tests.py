# coding=utf-8
import json

from django.urls import reverse
from django.test import TestCase


class TestUser(TestCase):
    def test_register(self):
        url = reverse("user-register")
        data = {
            'name': 'Jason',
            'phone': '18600138888',
            'password': '123456',
        }

        response = self.client.post(url, json.dumps(data), content_type="application/json")
        print(response)