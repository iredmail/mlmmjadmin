import web

from controllers.decorators import api_acl
from libs.utils import api_render
from libs import mlmmj, utils
import settings

# Load mailing list backend.
backend = __import__(settings.backend_api)


class Subscribers(object):
    @api_acl
    def GET(self, mail):
        """
        Get subscribers of different subscription versions.
        If no version given, return subscribers of all subscription versions.

        :param mail: email address of the mailing list account

        Available HTTP query parameters:

        :param email_only: if set to `yes`, return a list of subscribers' mail
                           addresses. otherwise return a dict:
                           {'<subscription1>': [<mail>, <mail>, ...],
                            '<subscription2>': [<mail>, <mail>, ...],
                            '<subscription3>': [<mail>, <mail>, ...]}
        """
        # Get extra parameters.
        qr = mlmmj.get_subscribers(mail=mail)
        return api_render(qr)

    @api_acl
    def POST(self, mail):
        """
        Add multiple subscribers to given subscription version.

        @mail -- email address of the mailing list account
        @subscription -- possible subscription versions: normal, digest, nomail.

        Available parameters:

        @subscribers -- email address of subscriber. Multiple subscribers must
                        be separated by comma.
        """
        form = web.input()

        if 'add_subscribers' in form:
            subscribers = form.get('add_subscribers', '').replace(' ', '').split(',')
            subscribers = [str(i).lower() for i in subscribers if utils.is_email(i)]

            require_confirm = True
            if form.get('require_confirm') != 'yes':
                require_confirm = False

            subscription = form.get('subscription', 'normal')
            if subscription not in ['normal', 'digest', 'nomail']:
                subscription = 'normal'

            qr = mlmmj.add_subscribers(mail=mail,
                                       subscribers=subscribers,
                                       subscription=subscription,
                                       require_confirm=require_confirm)

            if not qr[0]:
                return api_render(qr)

        if 'remove_subscribers' in form:
            if form.get('remove_subscribers') == 'ALL':
                qr = mlmmj.remove_all_subscribers(mail=mail)
            else:
                subscribers = form.get('remove_subscribers', '').replace(' ', '').split(',')
                subscribers = [str(i).lower() for i in subscribers if utils.is_email(i)]

                qr = mlmmj.remove_subscribers(mail=mail, subscribers=subscribers)

            if not qr[0]:
                return api_render(qr)

        return api_render(True)


class SubscribedLists(object):
    @api_acl
    def GET(self, subscriber):
        """Get mailing lists which the given subscriber subscribed to.

        HTTP GET Parameters:

        :param query_all_lists: If set to 'yes', will check all available
                                mailing lists on server. If 'no', check only
                                lists under same domain.
        """
        subscriber = str(subscriber).lower()
        domain = subscriber.split('@', 1)[-1]

        form = web.input(_unicode=False)

        email_only = False
        if form.get('email_only') == 'yes':
            email_only = True

        # Get mail addresses of existing accounts
        if form.get('query_all_lists') == 'yes':
            qr = backend.get_existing_maillists(domains=None)
        else:
            qr = backend.get_existing_maillists(domains=[domain])

        if not qr[0]:
            return api_render(qr)

        existing_lists = qr[1]
        if not existing_lists:
            return api_render((True, []))

        subscribed_lists = []
        for i in existing_lists:
            qr = mlmmj.has_subscriber(mail=i,
                                      subscriber=subscriber,
                                      subscription=None)
            if qr:
                if email_only:
                    subscribed_lists.append(i)
                else:
                    subscribed_lists.append({'subscription': qr[1], 'mail': i})

        return api_render((True, list(subscribed_lists)))


class Subscribe(object):
    @api_acl
    def POST(self, subscriber):
        """
        Add one subscriber to multiple mailing lists.

        :param mail: email address of the subscriber

        Available POST parameters:

        :param lists: mailing lists. Multilple mailing lists must be separated
                      by comma.
        :param require_confirm: [yes|no]. If set to `no`, will not send
                                subscription confirm to subscriber. Defaults to
                                `yes`.
        :param subscription: possible subscription versions: normal, digest, nomail.
        """
        subscriber = str(subscriber).lower()

        form = web.input(_unicode=False)

        subscription = form.get('subscription', 'normal')
        if subscription not in mlmmj.subscription_versions:
            subscription = 'normal'

        # Get mailing lists
        lists = form.get('lists', '').replace(' ', '').split(',')
        lists = [str(i).lower() for i in lists if utils.is_email(i)]

        require_confirm = True
        if form.get('require_confirm') == 'no':
            require_confirm = False

        qr = mlmmj.subscribe_to_lists(subscriber=subscriber,
                                      lists=lists,
                                      subscription=subscription,
                                      require_confirm=require_confirm)

        return api_render(qr)
