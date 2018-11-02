# -*- coding: utf-8 -*-
import json
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from rest_framework_jwt.settings import api_settings

from scoreserver import models, factories, views

factory = APIRequestFactory()

class UserApiTest(APITestCase):

    def setUp(self):
        factories.create_questions(10, flags=3, hints=2, categories=3, tags=3)
        for _ in range(10):
            factories.TeamFactory.create(users=3)

        self.test_team = models.Team.objects.all().order_by("?")[0]
        for user in self.test_team.users.all():
            for solvelog in user.solvelog_set.all():
                solvelog.delete()

    def test_create_team(self):
        url = reverse("scoreserver:team-list")
        view = views.TeamViewSet.as_view({
            'post': 'create'
        })

        request = factory.post(url, dict(
            name='TeamFlagger',
            email='flagger@example.com',
            password='teamflaggerpw'
        ))

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        teams = models.Team.objects.filter(name='TeamFlagger', email='flagger@example.com')
        self.assertEqual(len(teams), 1)

        team = teams[0]
        self.assertTrue(team.check_password('teamflaggerpw'))
        self.assertEqual(team.score, 0)

    def test_create_user(self):
        url = reverse("scoreserver:user-list")
        view = views.UserViewSet.as_view({
            'post': 'create'
        })

        request = factory.post(url, dict(
            team_name=self.test_team.name,
            team_password='teampasswd',
            username='newuser',
            password='newpasswd',
        ))

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        users = models.User.objects.filter(username='newuser', team=self.test_team)
        self.assertEqual(len(users), 1)

        user = users[0]
        self.assertTrue(user.check_password('newpasswd'))
        self.assertEqual(user.score, 0)
        self.assertEqual(user.team.score, 0)
