# -*- coding: utf-8 -*-
from django.urls import path, include

from scoreserver import views

app_name = "scoreserver"
urlpatterns = views.router.urls
urlpatterns.append(path("submit/", views.SubmitViewSet.as_view(), name="submit"))
