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
        form = web.input(subscriber=[], _unicode=False)
        subscribers = form.get('subscribers', '').replace(' ', '').split(',')
        subscribers = [str(i).lower() for i in subscribers if utils.is_email(i)]

        qr = mlmmj.remove_subscribers(mail=mail, subscribers=subscribers, subscription=subscription)

        return api_render(qr)

    @api_acl
    def DELETE(self, mail, subscription):
        """
        Remove ALL subscribers from all subscription versions.

        :param mail: email address of the mailing list account
        :param subscription: 'ALL'. Remove all subscribers in all subscription
                             versions.
        """
        if subscription == 'ALL':
            qr = mlmmj.remove_all_subscribers(mail=mail)
            return api_render(qr)
        else:
            return api_render(True)


class AddSubscribers(object):
    @api_acl
    def POST(self, mail, subscription):
        """
        Add multiple subscribers to given subscription version.

        @mail -- email address of the mailing list account
        @subscription -- possible subscription versions: normal, digest, nomail.

        Available parameters:

        @subscribers -- email address of subscriber. Multiple subscribers must
                        be separated by comma.
        """
        form = web.input()

        require_confirm = True
        if form.get('require_confirm') != 'yes':
            require_confirm = False

        subscribers = form.get('subscribers', '').replace(' ', '').split(',')
        subscribers = [str(i).lower() for i in subscribers if utils.is_email(i)]

        qr = mlmmj.add_subscribers(mail=mail,
                                   subscribers=subscribers,
                                   subscription=subscription,
                                   require_confirm=require_confirm)

        return api_render(qr)
