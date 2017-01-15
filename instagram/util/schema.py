# coding=utf-8


def optional_dict(data, keys):
    return {k: data[k] for k in data if k in keys}
