# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from scoreserver import models, factories


class Command(BaseCommand):
    def __init__(self):
        super().__init__()

    def create_notice(self, num):
        factories.NoticeFactory.create_batch(num)

    def create_question(self, num):
        factories.create_questions(num, flags=3, hints=2, categories=3, tags=3)

    def create_team(self, num):
        for _ in range(num):
            factories.TeamFactory.create(users=4)

    def create_superuser(self):
        user = models.User.objects.create_superuser(username="tukejonny", email="tukejonny@example.com", password="tukejonny")
        user.save()

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', default=10, type=int, help='Number of each model\'s seed data')

    def handle(self, *args, **options):
        num = options['num']

        self.create_superuser()
        self.create_question(num)
        self.create_team(num)
        self.create_notice(num)
