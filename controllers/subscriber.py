import web

from controllers.decorators import api_acl
from libs.utils import api_render
from libs import mlmmj, utils
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


class RemoveSubscriber(object):
    @api_acl
    def DELETE(self, mail, subscription, subscriber):
        """
        Remove single subscriber from given subscription version.

        @mail -- email address of the mailing list account
        @subscription -- possible subscription versions: normal, digest, nomail.
        @subscriber -- email address of subscriber
        """
        qr = mlmmj.remove_subscriber(mail=mail, subscriber=subscriber, subscription=subscription)
        return api_render(qr)


class RemoveSubscribers(object):
    @api_acl
    def POST(self, mail, subscription):
        """
        Remove single subscriber from given subscription version.

        @mail -- email address of the mailing list account
        @subscription -- possible subscription versions: normal, digest, nomail.
        """
        form = web.input(subscriber=[])
        subscribers = [str(i).lower() for i in form.get('subscriber', []) if utils.is_email(i)]
        print 10, 'subscribers:', subscribers

        qr = mlmmj.remove_subscribers(mail=mail, subscribers=subscribers, subscription=subscription)
        return api_render(qr)
