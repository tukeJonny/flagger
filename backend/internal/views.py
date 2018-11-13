# -*- coding: utf-8 -*-
import json

import django_filters
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import routers
from rest_framework import generics, viewsets, mixins, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_jwt import authentication as jwt_authentication

from scoreserver import models, serializers
from scoreserver.permissions import IsCTFOpened, IsCTFEnded

router = routers.SimpleRouter()

class UserRankingViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def list(self, request):
        ranking = models.SolveLog.objects.get_user_ranking()
        return HttpResponse(json.dumps(ranking), status=status.HTTP_200_OK)

router.register("user_ranking", UserRankingViewSet, base_name="user_ranking")
