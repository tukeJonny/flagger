# -*- coding: utf-8 -*-
from django.db.models import Sum
from django.test import TestCase

from scoreserver import models, factories

class SolveLogModelTest(TestCase):

    def setUp(self):
        factories.create_questions(10, flags=3, hints=2, categories=3, tags=3)
        for _ in range(10):
            factories.TeamFactory.create(users=3)

        self.total_score = models.SolveLog.objects.aggregate(Sum('flag__point'))['flag__point__sum']

    def test_get_user_ranking(self):
        user_ranking = models.SolveLog.objects.get_user_ranking()
        self.assertTrue(isinstance(user_ranking, list))

        user_ranking_total_score = 0
        before_user_score = 10000
        for user_rank in user_ranking:
            self.assertTrue(isinstance(user_rank, dict))
            self.assertTrue('rank' in user_rank)
            self.assertTrue('username' in user_rank)
            self.assertTrue('score' in user_rank)

            user_score = user_rank['score']
            self.assertTrue(user_score <= before_user_score)

            before_user_score = user_score
            user_ranking_total_score += user_score

        self.assertEqual(user_ranking_total_score, self.total_score)

    def test_get_team_ranking(self):
        team_ranking = models.SolveLog.objects.get_team_ranking()
        self.assertTrue(isinstance(team_ranking, list))

        team_ranking_total_score = 0
        before_team_score = 10000
        for team_rank in team_ranking:
            self.assertTrue(isinstance(team_rank, dict))
            self.assertTrue('rank' in team_rank)
            self.assertTrue('teamname' in team_rank)
            self.assertTrue('score' in team_rank)

            team_score = team_rank['score']
            self.assertTrue(team_score <= before_team_score)

            before_team_score = team_score
            team_ranking_total_score += team_score

        self.assertEqual(team_ranking_total_score, self.total_score)
