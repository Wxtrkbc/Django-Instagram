# -*- coding: utf-8 -*-

from django.conf.urls import url

from app.views import InsViewSet


urlpatterns = [
    url('^$', InsViewSet.as_view({
        'post': 'create_ins',
    }), name='create-ins'),

    url('^(?P<uuid>[0-9a-f-]{36})$', InsViewSet.as_view({
        'delete': 'delete_ins'
    }), name='delete-ins')
]
