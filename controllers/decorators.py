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
    def guard_func(self, *args, **kw)
        try:
            client_ip = web.ctx.ip
        except:
            # No `ip` attr before starting http service.
            return None

        if not _is_allowed_client(client_ip):
            logger.error('[{0}] Blocked request from disallowed client.'.format(client_ip))
            return api_render((False, 'NOT_AUTHORIZED_API_CLIENT'))

        _auth_token = get_auth_token()
        if not _auth_token:
            return api_render((False, 'NO_API_AUTH_TOKEN'))
        else:
            logger.debug('[{0}] API AUTH TOKEN: {1:.8}...'.format(client_ip, _auth_token))

        if _auth_token not in settings.api_auth_tokens:
            logger.error('[{0}] Blocked request with invalid auth token: {1}.'.format(client_ip, _auth_token))
            return api_render((False, 'INVALID_MLMMJADMIN_API_AUTH_TOKEN'))

        return func(self, *args, **kw)

    return guard_func
