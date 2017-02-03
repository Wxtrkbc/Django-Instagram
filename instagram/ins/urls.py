# coding=utf-8

from rest_framework.routers import DefaultRouter

from user.views import UserViewSet
from app.views import InsViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)   # ^users/{pk}/$ Name: 'user-detail'
router.register(r'ins', InsViewSet)

urlpatterns = router.urls
