# coding=utf-8

from util.exception import INSException
from util import errors


def optional_dict(data, keys):
    return {k: data[k] for k in data if k in keys}


def validate_value(value, choices):
    vs = [x[0] for x in list(choices)] if isinstance(choices, tuple) else choices
    if value not in vs:
        raise INSException(code=errors.ERR_INVALID_VALUE,
                           message='Invalid value {}, possible choices: {} '.format(value, vs))
