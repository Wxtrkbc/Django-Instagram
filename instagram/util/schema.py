# coding=utf-8

from django.shortcuts import get_object_or_404
from django.http import Http404

from util.exception import INSException
from util import errors


def validate_value(value, choices):
    vs = [x[0] for x in list(choices)] if isinstance(choices, tuple) else choices
    if value not in vs:
        raise INSException(code=errors.ERR_INVALID_VALUE,
                           message='Invalid value {}, possible choices: {} '.format(value, vs))


def check_body_keys(data, keys):
    keys = check_missing_keys(data, keys)
    if not keys:
        return
    raise INSException(code=errors.ERR_MISSING_BODY_FIELD,
                       message='Missing required field in request body: {}'.format(keys))


def check_params_keys(params, keys, exclusion=False):
    if not exclusion:
        missing_keys = check_missing_keys(params, keys)
        if missing_keys:
            raise INSException(message='Missing required query params: {}'.format(missing_keys),
                               code=errors.ERR_MISSING_QUERY_PARAMS)
        return
    for key in keys:
        if key in params:
            return
    raise INSException(message='Missing required query params(or): {}'.format(keys),
                       code=errors.ERR_MISSING_QUERY_PARAMS)


def optional_dict(data, keys):
    return {k: data[k] for k in data if k in keys}


def check_missing_keys(data, keys):
    return [key for key in keys if key not in data]


def get_object_or_400(klass, *args, **kwargs):
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Http404 as ex:
        raise INSException(code=errors.ERR_OBJECT_NOT_FOUND, message=ex.message)
