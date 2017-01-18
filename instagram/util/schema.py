# coding=utf-8

from django.shortcuts import get_object_or_404
from django.http import Http404

from util.exception import INSException
from util import errors


def optional_dict(data, keys):
    return {k: data[k] for k in data if k in keys}


def validate_value(value, choices):
    vs = [x[0] for x in list(choices)] if isinstance(choices, tuple) else choices
    if value not in vs:
        raise INSException(code=errors.ERR_INVALID_VALUE,
                           message='Invalid value {}, possible choices: {} '.format(value, vs))


def get_object_or_400(klass, *args, **kwargs):
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Http404 as ex:
        raise INSException(code=errors.ERR_OBJECT_NOT_FOUND, message=ex.message)
