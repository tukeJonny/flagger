# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Sum, Count
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password


# Base
class AbstractBaseModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Notice
class NoticeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)

class Notice(AbstractBaseModel):

    class Meta:
        db_table = 'notices'
        ordering=('-updated_at',)

    title = models.CharField(max_length=255)
    description = models.TextField()

    is_public = models.BooleanField()

    objects = NoticeManager()

    def __str__(self):
        return self.title

# Player
## Register Team -> Login Team & Register User

class TeamManager(models.Manager):

    def get_queryset_solo_user(self):
        self.get_queryset().annotate(number_of_users=Count('users')).filter(number_of_users=1)

class Team(AbstractBaseModel):

    class Meta:
        db_table = 'teams'

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    objects = TeamManager()

    @property
    def score(self):
        return SolveLog.objects.get_team_score(team=self)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        def setter(raw_password):
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    def __str__(self):
        return self.name

class User(AbstractUser, AbstractBaseModel):

    class Meta:
        db_table = 'users'

    team = models.ForeignKey(Team, related_name='users', on_delete=models.CASCADE, null=True)
    ip = models.CharField(max_length=255)
    is_banned = models.BooleanField(default=False, unique=False)

    @property
    def score(self):
        return SolveLog.objects.get_user_score(user=self)

# Question

class Category(AbstractBaseModel):

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Tag(AbstractBaseModel):

    class Meta:
        db_table = 'tags'

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class QuestionManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)

    def get_queryset_by_category_name(self, category_name):
        return self.get_queryset().filter(categories__name=category_name)

    def get_queryset_by_tag_name(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name)

class Question(AbstractBaseModel):

    class Meta:
        db_table = 'questions'

    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)

    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=255)
    solved_cnt = models.IntegerField(default=0)
    trial_cnt = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False, unique=False)

    objects = QuestionManager()

    @property
    def solved_rate(self):
        return (solved_cnt / trial_cnt) * 100

class FlagManager(models.Manager):

    def get_submitted_or_none(self, question, flag_str):
        """フラグ提出を審査"""
        try:
            flag = Flag.objects.get(question=question, flag=flag_str)
            return flag
        except ObjectDoesNotExist:
            return None

class Flag(AbstractBaseModel):

    class Meta:
        db_table = 'flags'

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    flag = models.CharField(max_length=255, unique=True)
    point = models.IntegerField()

    objects = FlagManager()

    def __str__(self):
        return "{} ({}pt)".format(self.question.title, self.point)

class HintManager(models.Manager):

    def get_queryset(self):
    	return self.get_queryset().filter(is_public=True)

class Hint(AbstractBaseModel):

    class Meta:
        db_table = 'hints'
        ordering = ('-updated_at',)

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    description = models.TextField()
    is_public = models.BooleanField(default=False, unique=False)

## Log

class SolveLogManager(models.Manager):

    def get_queryset_by_flags(self, flags):
        return self.get_queryset().filter(flag__in=flag)

    def is_duplicate_submission(self, team, flag):
        """フラグの重複提出(チーム単位)を行ってしまっているか"""
        return self.get_queryset().filter(team=team, flag=flag).exists()

    def get_team_score(self, team):
        score = self.get_queryset().filter(team=team).aggregate(score=Sum('flag__point'))['score']
        if score is None:
            return 0
        return score

    def get_user_score(self, user):
        score = self.get_queryset().filter(user=user).aggregate(score=Sum('flag__point'))['score']
        if score is None:
            return 0
        return score

    # NOTE: 得点しているチームのみのランキング
    def get_team_ranking(self):
        # we can't chain queryset
        qs = self.get_queryset().values('team__name').annotate(score=Sum('flag__point')).order_by('-score')
        return [dict(rank=idx+1, teamname=d['team__name'], score=d['score']) for idx, d in enumerate(qs)]

    def get_user_ranking(self):
        # we can't chain queryset
        qs = self.get_queryset().values('user__username').annotate(score=Sum('flag__point')).order_by('-score')
        return [dict(rank=idx+1, username=d['user__username'], score=d['score']) for idx, d in enumerate(qs)]

    def get_solo_user_ranking(self):
        # we can't chain queryset
        teams = Team.objects.get_queryset_solo_user()
        qs = self.get_queryset().filter(team__in=teams).values('team__name', 'user__username').annotate(score=Sum('flag__point')).order_by('-score')
        return [dict(rank=idx+1, username=d['user__username'], teamname=d['team__name'], score=d['score']) for idx, d in enumerate(qs)]

class SolveLog(AbstractBaseModel):

    class Meta:
        db_table = 'solve_logs'

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flag = models.ForeignKey(Flag, on_delete=models.CASCADE)

    objects = SolveLogManager()

    def __str__(self):
        return self.user.username
