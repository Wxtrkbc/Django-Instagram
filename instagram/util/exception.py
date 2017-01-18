# coding=utf-8

from django.utils.deprecation import MiddlewareMixin

from util.response import json_response, error_response
from util.errors import ERR_CODE_MAP


class INSException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super(INSException, self).__init__(message)

    def __str__(self):
        return 'code: {}, message: {}'.format(self.code, self.message)


class INSExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if type(exception) == INSException:
            if type(exception.code) == int:
                return error_response(message=exception.message, status=exception.code)
            return json_response(data={
                'message': exception.message,
                'code': exception.code,
            }, status=get_status_code(exception.code))


def get_status_code(err_code):
    return 400 if err_code not in ERR_CODE_MAP else ERR_CODE_MAP[err_code]
