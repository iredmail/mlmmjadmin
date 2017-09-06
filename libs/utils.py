# encoding: utf-8
import sys
import web

if sys.version_info >= (2, 6):
    import json
else:
    import simplejson as json

from libs import regxes
import settings

# API AUTH token name in http request header
auth_token_name = 'HTTP_' + settings.API_AUTH_TOKEN_HEADER_NAME.replace('-', '_').upper()

def is_email(s):
    try:
        s = str(s).strip()
    except UnicodeEncodeError:
        return False

    # Not contain invalid characters and match regular expression
    if regxes.cmp_email.match(s):
        return True

    return False

def is_domain(s):
    try:
        s = str(s).lower()
    except:
        return False

    if len(set(s) & set('~!#$%^&*()+\\/\ ')) > 0 or '.' not in s:
        return False

    if regxes.cmp_domain.match(s):
        return True
    else:
        return False

def get_auth_token():
    _token = web.ctx.env.get(auth_token_name)
    return _token


def _render_json(d):
    web.header('Content-Type', 'application/json')
    return json.dumps(d)


def api_render(data):
    """Convert given data to a dict and render it."""
    if isinstance(data, dict):
        d = data
    elif isinstance(data, tuple):
        if data[0] is True:
            if len(data) == 2:
                d = {'_success': True, '_data': data[1]}
            else:
                d = {'_success': True}
        else:
            if len(data) == 2:
                d = {'_success': False, '_msg': data[1]}
            else:
                d = {'_success': False}

    elif isinstance(data, bool):
        d = {'_success': data}

    return _render_json(d)
