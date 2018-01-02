# URL mappings
from libs.regxes import email as e

urls = [
    # Per-maillist profile
    '/api/({})$'.format(e), 'controllers.profile.Profile',

    #
    # Per-maillist subscribers
    #
    # Get subscribers.
    '/api/({})/subscribers'.format(e), 'controllers.subscriber.Subscribers',

    #
    # per-subscriber
    #
    # Get all subscribed mailing lists of given subscriber.
    '/api/subscriber/({})/subscribed'.format(e), 'controllers.subscriber.SubscribedLists',
    # Subscribe one subscriber to multiple mailing lists.
    '/api/subscriber/({})/subscribe'.format(e), 'controllers.subscriber.Subscribe',
]
