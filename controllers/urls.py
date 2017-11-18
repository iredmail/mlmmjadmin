# URL mappings
from libs.regxes import email as e

urls = [
    # Per-maillist profile
    '/api/({})$'.format(e), 'controllers.apis.MLProfile',
]
