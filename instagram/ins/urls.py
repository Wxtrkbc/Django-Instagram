# coding=utf-8

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet
from app.views import InsViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)   # ^users/{pk}/$ Name: 'user-detail'
router.register(r'ins', InsViewSet)

urlpatterns = [
    url(r'^ins/', include('app.urls'))
]

urlpatterns += router.urls
