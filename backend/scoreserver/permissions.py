# -*- coding: utf-8 -*-
from datetime import datetime
import os
import importlib
from rest_framework.permissions import BasePermission

settings = importlib.import_module(os.getenv("DJANGO_SETTINGS_MODULE"))
from scoreserver import exceptions

class IsCTFOpened(BasePermission):

    def has_permission(self, request, view):
        start = settings.CONSTANCE_CONFIG['CTF_START_AT']
        end = settings.CONSTANCE_CONFIG['CTF_END_AT']

        now = datetime.now()
        if now < start[0]:
            raise exceptions.OutOfTermException(message='CTF haven\'t started yet.', code='not_start')
        elif now > end[0]:
            raise exceptions.OutOfTermException(message='CTF had already ended.', code='ended')

        return True

class IsCTFEnded(BasePermission):

    def has_permission(self, request, view):
        end = settings.CONSTANCE_CONFIG['CTF_END_AT']

        now = datetime.now()
        if now < end[0]:
            raise exceptions.OutOfTermException(message='CTF haven\'t started yet.', code='not_start')
