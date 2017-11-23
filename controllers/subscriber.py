import web

from controllers.decorators import api_acl
from libs.utils import api_render
from libs import mlmmj
import settings

# Load mailing list backend.
backend = __import__(settings.backend)


class Subscribers(object):
    @api_acl
    def GET(self, mail, subscription=None):
        """
        Get subscribers of different subscription versions.
        If no version given, return subscribers of all subscription versions.

        @mail -- email address of the mailing list account
        @version -- possible subscription versions: normal, digest, nomail.
        """
        if subscription not in mlmmj.subscription_versions:
            return api_render((False, 'INVALID_SUBSCRIPTION_VERSION'))

        # Get extra parameters.
        form = web.input(_unicode=False)

        combined = False
        if form.get('combined', 'no') == 'yes':
            combined = True

        qr = mlmmj.get_subscribers(mail=mail, subscription=subscription, combined=combined)
        return api_render(qr)

    @api_acl
    def PUT(self, mail, subscription):
        """
        Add new subscribers in specified subscription version.

        @mail -- email address of the mailing list account
        @version -- possible subscription versions: normal, digest, nomail.
        """
        pass
