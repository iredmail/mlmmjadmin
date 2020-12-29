#!/usr/bin/env python3
# Sync few mailing list profiles to SQL/LDAP db, including:
#
#   - access policy (SQL table: vmail.maillists)
#   - moderators (SQL table: vmail.moderators)
#   - members (SQL table: vmail.maillist_members)
#   - owners (SQL table: vmail.maillist_owners)

import sys
import os
import web
web.config.debug = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../backends')

from libs.utils import is_email
import settings

usage = """Usage:

    python3 sync_profiles_to_db.py [-A] [email] [email] [...]

Samples:

    *) Sync all mailing lists (note: `-A` in upper case, not `-a`):

        python3 sync_profiles_to_db.py -A

    *) Sync only one mailing list:

        python3 sync_profiles_to_db.py list@domain.com

    *) Sync multiple mailing lists:

        python3 sync_profiles_to_db.py list1@domain.com list2@domain.com list3@domain.com

"""

# Base url of API interface
api_base_url = 'http://127.0.0.1:{0}/api'.format(settings.listen_port)

# Don't verify ssl cert. useful for self-signed ssl cert.
verify_ssl = False

# Use first auth token
api_auth_token = settings.api_auth_tokens[0]
api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: api_auth_token}

# Load mailing list backend.
run_backend_cli = False
backend = None
if settings.backend_api == 'bk_none':
    run_backend_cli = True
    backend = __import__(settings.backend_cli)

mls = []
args = sys.argv[1:]
if args[0] == '-A':
    # Query db to get all mailing lists.
    pass
else:
    # Get target MLs from command line.
    mls = [i.lower() for i in mls if is_email(i)]

# Get profiles of each mailing list.
# Sync profile to SQL/LDAP db.
