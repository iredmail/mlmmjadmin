# URL mappings
from libs.regxes import email as e

urls = [
    # Per-maillist profile
    '/api/({})$'.format(e), 'controllers.profile.Profile',

    #
    # Subscribers
    #
    # Get subscribers in all subscription versions
    '/api/({})/subscribers$'.format(e), 'controllers.subscriber.Subscribers',
    # Get subscribers in particular subscription version
    '/api/({})/subscribers/(normal|nomail|digest)$'.format(e), 'controllers.subscriber.Subscribers',
    # Remove single subscriber
    '/api/({})/remove_subscriber/(normal|nomail|digest)/({})$'.format(e, e), 'controllers.subscriber.RemoveSubscriber',
]
