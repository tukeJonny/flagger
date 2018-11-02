# -*- coding: utf-8 -*-

import django.dispatch
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from scoreserver import models


correct_submission = django.dispatch.Signal(providing_args=["team", "user", "question", "flag_str"])
incorrect_submission = django.dispatch.Signal(providing_args=["team", "user", "question", "flag_str"])

@receiver(correct_submission)
def correct_submission_handler(sender, **kwargs):
    print("[+] Correct:", kwargs['team'].name, kwargs['user'].username, kwargs['question'].title, kwargs['flag_str'])

@receiver(incorrect_submission)
def incorrect_submission_handler(sender, **kwargs):
    print("[-] Incorrect:", kwargs['team'].name, kwargs['user'].username, kwargs['question'].title, kwargs['flag_str'])

