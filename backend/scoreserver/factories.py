# -*- coding: utf-8 -*-
import random
import logging
logging.getLogger("factory").setLevel(logging.INFO)

from django.contrib.auth.hashers import make_password
import factory
import factory.fuzzy

from scoreserver import models

def generate_ip():
    return '.'.join([str(random.randint(10, 254)) for _ in range(4)])

class NoticeFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Notice

    title = factory.Sequence(lambda idx: "notice{}".format(idx))
    description = factory.fuzzy.FuzzyText(length=50)

    is_public = True

class SolveLogFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.SolveLog

class UserFactory(factory.DjangoModelFactory):
    password = 'userpasswd'

    class Meta:
        model = models.User

    username = factory.Sequence(lambda idx: "user{}".format(idx))
    password = make_password(password)
    ip = factory.fuzzy.FuzzyAttribute(generate_ip)
    is_banned = False

class TeamFactory(factory.DjangoModelFactory):
    password = 'teampasswd'

    class Meta:
        model = models.Team

    name = factory.Sequence(lambda idx: "team{}".format(idx))
    email = factory.LazyAttribute(lambda o: "{}@example.com".format(o.name))
    password = make_password(password)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        """TeamFactory(users=10)"""
        if not create:
            return
        elif extracted:
            for _ in range(extracted):
                user = UserFactory(team=self)
                solved_questions = models.Question.objects.all().order_by("?")[:extracted]
                for solved_question in solved_questions:
                    flag = solved_question.flag_set.all()[0]
                    SolveLogFactory.create(team=self, user=user, flag=flag) # question=flag.question, flag=flag)

                    solved_question.solved_cnt += 1
                    solved_question.trial_cnt += 2
                    solved_question.save()

class CategoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Category

    name = factory.Sequence(lambda idx: "category{}".format(idx))

class TagFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Tag

    name = factory.Sequence(lambda idx: "tag{}".format(idx))

class FlagFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Flag

    flag = factory.Sequence(lambda idx: "FLAGGER_CTF{{HOGE_{}_FUGA}}".format(idx))
    point = factory.fuzzy.FuzzyInteger(100, 1000, 100)

class HintFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Hint

    description = factory.fuzzy.FuzzyText(length=50)

    is_public = True

class QuestionFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Question

    title = factory.Sequence(lambda idx: "question{}".format(idx))
    description = factory.fuzzy.FuzzyText(length=50)
    author = factory.Sequence(lambda idx: "author{}".format(idx))

    is_public = True

    @factory.post_generation
    def flags(self, create, extracted, **kwargs):
        """QuestionFactory(flags=10)"""
        if not create:
            return
        elif extracted:
            for i in range(extracted):
                FlagFactory(question=self, flag=self.title+str(i))
        else:
            for i in range(random.randint(1,10)):
                FlagFactory(question=self, flag=self.title+str(i))

    @factory.post_generation
    def hints(self, create, extracted, **kwargs):
        """QuestionFactory(hints=10)"""
        if not create:
            return
        elif extracted:
            for _ in range(extracted):
                HintFactory(question=self)
        else:
            for _ in range(random.randint(1,10)):
                HintFactory(question=self)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return
        elif extracted:
            for category in extracted:
                self.categories.add(category)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        elif extracted:
            for tag in extracted:
                self.tags.add(tag)


def create_questions(num, flags=3, hints=3, categories=3, tags=3):
    CategoryFactory.create_batch(10)
    TagFactory.create_batch(10)

    questions = []
    for _ in range(num):
        c = models.Category.objects.all().order_by("?")[:categories]
        t = models.Tag.objects.all().order_by("?")[:tags]
        question = QuestionFactory.create(flags=flags, hints=hints, categories=c, tags=t)
        questions.append(question)

    return questions
