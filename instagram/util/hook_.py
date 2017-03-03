import hashlib
from django.core.signing import TimestampSigner
from django.conf import settings
from django.contrib.auth import get_user_model

import requests
from rest_framework.renderers import JSONRenderer


User = get_user_model()


def _build_hook_url(obj):
    model_name = 'user' if isinstance(obj, User) else obj.__class__.__name__.lower()
    return "{}://{}/{}/{}".format(
        'https' if settings.WEBSOCKET_SECURE else 'http',
        settings.WEBSOCKET_SERVER, model_name, obj.pk
    )


def _build_hook_signature(method, url, body):
    signer = TimestampSigner(settings.WEBSOCKET_SECRET)
    value = '{method}:{url}:{body}'.format(
        method=method.lower(),
        url=url,
        body=hashlib.sha256(body or b'').hexdigest()
    )
    return signer.sign(value)


def send_hook_request(obj, method, context=None, data=None):
    url = _build_hook_url(obj)
    if method in ('POST', 'PUT', 'PATCH'):
        serializer = data
        render = JSONRenderer()
        context = context
        body = render.render(serializer.data, renderer_context=context)
    else:
        body = None

    headers = {
        'content-type': 'application/json',
        'X-Signature': _build_hook_signature(method, url, body)
    }
    try:
        response = requests.request(method, url, data=body, timeout=0.5, headers=headers)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException:
        # 4xx or 5xx
        pass
