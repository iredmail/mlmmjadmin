# URL mappings
from libs.regxes import email as e

urls = [
    # Per-maillist profile
    '/api/({})$'.format(e), 'controllers.profile.Profile',

    #
    # Subscribers
    #
    # Get subscribers in all subscription versions
    #'/api/({})/subscribers$'.format(e), 'controllers.subscriber.Subscribers',
    # Get subscribers in particular subscription version
    '/api/({})/subscribers/(normal|nomail|digest)$'.format(e), 'controllers.subscriber.Subscribers',
    # Remove single subscriber
    '/api/({})/remove_subscriber/(normal|nomail|digest)/({})$'.format(e, e), 'controllers.subscriber.RemoveSubscriber',
    # Remove multiple or ALL subscribers
    '/api/({})/remove_subscribers/(normal|nomail|digest|ALL)$'.format(e), 'controllers.subscriber.RemoveSubscribers',

    # Get all subscribed mailing lists of given subscriber.
    '/api/subscriber/({})/subscribed/(normal|nomail|digest|ALL)$'.format(e), 'controllers.profile.SubscribedLists',
    # Add one subscriber to multiple mailing lists.
    '/api/subscriber/({})/subscribe/(normal|nomail|digest)$'.format(e), 'controllers.profile.Subscribe',
]
