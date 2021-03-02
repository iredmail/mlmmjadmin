# encoding: utf-8
import json
from typing import Union, List, Tuple, Set, Dict, Any
import web

from libs import regxes
import settings

# API AUTH token name in http request header
auth_token_name = 'HTTP_' + settings.API_AUTH_TOKEN_HEADER_NAME.replace('-', '_').upper()


def __str2bytes(s) -> bytes:
    """Convert `s` from string to bytes."""
    if isinstance(s, bytes):
        return s
    elif isinstance(s, str):
        return s.encode()
    elif isinstance(s, (int, float)):
        return str(s).encode()
    else:
        return bytes(s)


def str2bytes(s) -> bytes:
    """Convert `s` from string to bytes."""
    if isinstance(s, (list, web.db.ResultSet)):
        s = [str2bytes(i) for i in s]
    elif isinstance(s, tuple):
        s = tuple([str2bytes(i) for i in s])
    elif isinstance(s, set):
        s = {str2bytes(i) for i in s}
    elif isinstance(s, (dict, web.utils.Storage)):
        new_dict = {}
        for (k, v) in list(s.items()):
            new_dict[k] = str2bytes(v)  # v could be list/tuple/dict
        s = new_dict
    else:
        s = __str2bytes(s)

    return s


def __bytes2str(b) -> str:
    """Convert object `b` to string.

    >>> __bytes2str("a")
    'a'
    >>> __bytes2str(b"a")
    'a'
    >>> __bytes2str(["a"])  # list: return `repr()`
    "['a']"
    >>> __bytes2str(("a",)) # tuple: return `repr()`
    "('a',)"
    >>> __bytes2str({"a"})  # set: return `repr()`
    "{'a'}"
    """
    if isinstance(b, str):
        return b

    if isinstance(b, (bytes, bytearray)):
        return b.decode()
    elif isinstance(b, memoryview):
        return b.tobytes().decode()
    else:
        return repr(b)


def bytes2str(b: Union[bytes, str, List, Tuple, Set, Dict])\
        -> Union[str, List[str], Tuple[str], Dict[Any, str]]:
    """Convert `b` from bytes-like type to string.

    - If `b` is a string object, returns original `b`.
    - If `b` is a bytes, returns `b.decode()`.

    bytes-like object, return `repr(b)` directly.

    >>> bytes2str("a")
    'a'
    >>> bytes2str(b"a")
    'a'
    >>> bytes2str(["a"])
    ['a']
    >>> bytes2str((b"a",))
    ('a',)
    >>> bytes2str({b"a"})
    {'a'}
    >>> bytes2str({"a": b"a"})      # used to convert LDAP query result.
    {'a': 'a'}
    """
    if isinstance(b, list):
        s = [bytes2str(i) for i in b]
    elif isinstance(b, tuple):
        s = tuple([bytes2str(i) for i in b])
    elif isinstance(b, set):
        s = {bytes2str(i) for i in b}
    elif isinstance(b, dict):
        new_dict = {}
        for (k, v) in list(b.items()):
            new_dict[k] = bytes2str(v)  # v could be list/tuple/dict
        s = new_dict
    else:
        s = __bytes2str(b)

    return s


def strip_mail_ext_address(mail, delimiters=None):
    """Remove '+extension' in email address.

    >>> strip_mail_ext_address('user+ext@domain.com')
    'user@domain.com'
    """

    if not delimiters:
        delimiters = settings.RECIPIENT_DELIMITERS

    (_orig_user, _domain) = mail.split('@', 1)
    for delimiter in delimiters:
        if delimiter in _orig_user:
            (_user, _ext) = _orig_user.split(delimiter, 1)
            return _user + '@' + _domain

    return mail


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

    if len(set(s) & set(r'~!#$%^&*()+\/ ')) > 0 or ('.' not in s):
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
    else:
        d = {'_success': False, '_msg': 'INVALID_DATA'}

    return _render_json(d)
