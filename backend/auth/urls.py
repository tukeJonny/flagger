# -*- coding: utf-8 -*-
from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

app_name = "auth"
urlpatterns = [
    path('login/', obtain_jwt_token, name="login"),
    path('verify/', verify_jwt_token, name="verify"),
]
