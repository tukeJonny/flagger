# -*- coding: utf-8 -*-
import json
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from rest_framework_jwt.settings import api_settings

from scoreserver import models, factories, views

factory = APIRequestFactory()

class QuestionApiTest(APITestCase):

    def setUp(self):
        factories.create_questions(10, flags=3, hints=2, categories=3, tags=3)
        for _ in range(10):
            factories.TeamFactory.create(users=3)

        self.test_user = models.User.objects.all().order_by("?")[0]
        self.test_team = self.test_user.team
        for user in self.test_team.users.all():
            for solvelog in user.solvelog_set.all():
                solvelog.delete()

        self.test_question = models.Question.objects.all().order_by("?")[0]
        self.test_question.solved_cnt = 0
        self.test_question.trial_cnt = 0
        self.test_question.save()

        self.correct_flag = self.test_question.flag_set.all()[0]
        self.incorrect_flag = "FLAGGER_CTF{WRONG_FLAG}"

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        self.test_token = jwt_encode_handler(jwt_payload_handler(self.test_user))

    def test_correct_submit(self):
        url = reverse('scoreserver:submit')
        view = views.SubmitViewSet.as_view()

        # 正解フラグを投げたら、ログが記録され、チームの得点が正常に増えるはず
        request = factory.post(url, dict(
            question_id=self.test_question.id,
            flag_str=self.correct_flag.flag,
        ))

        before_team_score = self.test_team.score
        before_user_score = self.test_user.score

        force_authenticate(request, self.test_user, token=self.test_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'correct')
        self.assertEqual(models.SolveLog.objects.filter(team=self.test_team, flag=self.correct_flag).count(), 1)
        self.assertEqual(models.SolveLog.objects.filter(user=self.test_user, flag=self.correct_flag).count(), 1)

        expected_team_score = before_team_score + self.correct_flag.point
        expected_user_score = before_user_score + self.correct_flag.point
        self.assertEqual(self.test_team.score, expected_team_score)
        self.assertEqual(self.test_user.score, expected_user_score)

        self.test_question.refresh_from_db()
        self.assertEqual(self.test_question.solved_cnt, 1)
        self.assertEqual(self.test_question.trial_cnt, 1)


    def test_incorrect_submit(self):
        url = reverse('scoreserver:submit')
        view = views.SubmitViewSet.as_view()

        # 不正解フラグを投げたら、ログは記録されず、チームの得点は変わらないはず
        request = factory.post(url, dict(
            question_id=self.test_question.id,
            flag_str=self.incorrect_flag,
        ))

        before_team_score = self.test_team.score
        before_user_score = self.test_user.score

        force_authenticate(request, self.test_user, token=self.test_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'incorrect')
        self.assertEqual(models.SolveLog.objects.filter(team=self.test_team, flag=self.correct_flag).count(), 0)
        self.assertEqual(models.SolveLog.objects.filter(user=self.test_user, flag=self.correct_flag).count(), 0)

        self.assertEqual(self.test_team.score, before_team_score)
        self.assertEqual(self.test_user.score, before_user_score)

        self.test_question.refresh_from_db()
        self.assertEqual(self.test_question.solved_cnt, 0)
        self.assertEqual(self.test_question.trial_cnt, 1)
