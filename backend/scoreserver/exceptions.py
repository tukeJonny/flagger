# -*- coding: utf-8 -*-

from rest_framework.exceptions import APIException

class OutOfTermException(APIException):
    status_code = 503

    def __init__(self, message, code):
        super().__init__(dict(
            message=message,
            code=code
        ))
