# coding=utf-8

from rest_framework.routers import DefaultRouter

from user import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)   # ^users/{pk}/$ Name: 'user-detail'
