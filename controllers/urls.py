# URL mappings
from libs.regxes import email as e

urls = [
    # Per-maillist profile
    '/api/({})$'.format(e), 'controllers.apis.Profile',

    #
    # Subscribers
    #
    # Get subscribers in all subscription versions
    '/api/({})/subscribers$'.format(e), 'controllers.apis.Subscribers',
    # Get subscribers in particular subscription version
    '/api/({})/subscribers/(normal|nomail|digest)$'.format(e), 'controllers.apis.Subscribers',
]
