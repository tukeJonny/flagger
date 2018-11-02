import json

import django_filters
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import routers
from rest_framework import generics, viewsets, mixins, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt import authentication as jwt_authentication

from scoreserver import models, serializers, signals
from scoreserver.permissions import IsCTFOpened, IsCTFEnded

# Create your views here.

router = routers.SimpleRouter()

class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsCTFOpened,)
    serializer_class = serializers.NoticeSerializer
    queryset = models.Notice.objects.all()

router.register("notice", NoticeViewSet, base_name="notice")

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, IsCTFOpened)
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()

router.register("category", CategoryViewSet, base_name="category")

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, IsCTFOpened)
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()

router.register("tag", TagViewSet, base_name="tag")

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, IsCTFOpened)
    serializer_class = serializers.QuestionSerializer
    queryset = models.Question.objects.all()

router.register("question", QuestionViewSet, base_name="question")

class TeamViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsCTFOpened,)
    serializer_class = serializers.TeamSerializer

router.register("team", TeamViewSet, base_name="team")

class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    authentication_classes = (jwt_authentication.JSONWebTokenAuthentication,)
    permission_classes = (IsCTFOpened,)
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.filter(id=-1) # empty

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(team=self.request.user.team)

        return self.queryset

router.register("user", UserViewSet, base_name="user")

class SubmitViewSet(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsCTFOpened)
    serializer_class = serializers.SubmitSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        team = user.team
        question = get_object_or_404(models.Question, pk=data['question_id'])

        flag = models.Flag.objects.get_submitted_or_none(question, data['flag_str'])
        if flag is not None:
            if models.SolveLog.objects.is_duplicate_submission(team, flag):
                return HttpResponse('duplicate submission', status.HTTP_400_BAD_REQUEST)

            signals.correct_submission.send(sender=self.__class__, team=team, user=user, question=question, flag_str=data['flag_str'])

            question.solved_cnt = F('solved_cnt') + 1
            question.trial_cnt = F('trial_cnt') + 1
            question.save()

            solvelog = models.SolveLog.objects.create(team=team, user=user, flag=flag)
            solvelog.save()

            return HttpResponse('correct', status=status.HTTP_200_OK)
        else:
            signals.incorrect_submission.send(sender=self.__class__, team=team, user=user, question=question, flag_str=data['flag_str'])

            question.trial_cnt = F('trial_cnt') + 1
            question.save()

            return HttpResponse('incorrect', status=status.HTTP_200_OK)

class RankingViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsCTFOpened)

    def list(self, request):
        ranking = models.SolveLog.objects.get_team_ranking()
        return HttpResponse(json.dumps(ranking), status=status.HTTP_200_OK)

router.register("ranking", RankingViewSet, base_name="ranking")
