# -*- coding: utf-8 -*-
from django.http import HttpResponse

from rest_framework import status

class IPTrackingMiddleware:

    def process_request(self, request):
        if hasattr(request.META, 'HTTP_X_REAL_IP':
            ip = request.META.get('HTTP_X_REAL_IP')
        else:
            ip = request.META.get('REMOTE_ADDR')

        user = request.user
        if ip and user.is_authenticated():
            user.ip = ip
            user.save()

class BlockBannedUserMiddleware:

    def process_request(self, request):
        if request.user.is_banned:
            return HttpResponse('you are banned.', status.HTTP_403_FORBIDDEN)
