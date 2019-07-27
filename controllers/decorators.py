import web
import settings
from libs.utils import get_auth_token, api_render
from libs.logger import logger


def _is_allowed_client(ip):
    if settings.RESTRICT_ACCESS:
        if ip not in settings.ACCEPTED_CLIENTS:
            return False

    return True


def api_acl(func):
    def proxyfunc(self, *args, **kw):
        return func(self, *args, **kw)

    def empty(self, *args, **kw):
        return None

    def not_allowed_client(self, *args, **kw):
        return api_render((False, 'NOT_AUTHORIZED_API_CLIENT'))

    def no_auth_token(self, *args, **kw):
        return api_render((False, 'NO_API_AUTH_TOKEN'))

    def invalid_auth_token(self, *args, **kw):
        return api_render((False, 'INVALID_MLMMJADMIN_API_AUTH_TOKEN'))

    try:
        client_ip = web.ctx.ip
    except:
        # No `ip` attr before starting http service.
        return empty

    if not _is_allowed_client(client_ip):
        logger.error('[{0}] Blocked request from disallowed client.'.format(client_ip))
        return not_allowed_client

    _auth_token = get_auth_token()
    if not _auth_token:
        #if client_ip != '127.0.0.1':
        #    logger.error('[{0}] Blocked request without auth token.'.format(client_ip))
        return no_auth_token
    else:
        logger.debug('[{0}] API AUTH TOKEN: {1:.8}...'.format(client_ip, _auth_token))

    if _auth_token not in settings.api_auth_tokens:
        logger.error('[{0}] Blocked request with invalid auth token: {1}.'.format(client_ip, _auth_token))
        return invalid_auth_token

    return proxyfunc
