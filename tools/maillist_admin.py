# TODO list all mailing list accounts
#   - if `backend` is `bk_none`, list all accounts under mlmmj spool directory.
#   - if `backend` is not `bk_none`, query from backend.
import sys
import os
from urllib import urlencode
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from libs.utils import is_email
import settings

usage = """Usage:

    python maillist_admin.py <info|create|update|delete> <mail> [<param1>=<value1> <param2>=<value2> ...]

Samples:

    *) Get settings of an existing mailing list account

        python maillist_admin.py info list@domain.com

    *) Create a new mailing list account with additional setting:

        python maillist_admin.py create list@domain.com only_subscriber_can_post=yes disable_archive=no

    *) Update an existing mailing list account

        python maillist_admin.py update list@domain.com only_moderator_can_post=yes disable_subscription=yes

    *) Delete an existing mailing list account

        python maillist_admin.py delete list@domain.com

    *) Get subscribers which subscribed to `normal` version:

        python maillist_admin.py subscribers_normal list@domain.com

    *) Get subscribers which subscribed to `digest` version:

        python maillist_admin.py subscribers_digest list@domain.com

    *) Get subscribers which subscribed to `nomail` version:

        python maillist_admin.py subscribers_nomail list@domain.com
"""

if len(sys.argv) < 3:
    print usage
    sys.exit()

# Base url of API interface
api_base_url = 'http://127.0.0.1:{}/api'.format(settings.listen_port)

# Don't verify ssl cert. useful for self-signed ssl cert.
verify_ssl = False

# Use first auth token
api_auth_token = settings.api_auth_tokens[0]
api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: api_auth_token}

# Load mailing list backend.
backend = __import__(settings.backend_cli)

action = sys.argv[1]
if action not in ['info', 'create', 'update', 'delete',
                  'subscribers',
                  'subscribers_normal',
                  'subscribers_digest',
                  'subscribers_nomail']:
    sys.exit('Invalid action: {}, must be one of: info, create, update, delete.'.format(action))

mail = sys.argv[2]
if not is_email(mail):
    sys.exit('Invalid email address: {}'.format(mail))

args = sys.argv[3:]

# Convert args to a dict
arg_kvs = {}
for arg in args:
    if '=' in arg:
        (k, v) = arg.split('=', 1)
        arg_kvs[k] = v

api_url = api_base_url + '/' + mail

if action == 'info':
    r = requests.get(api_url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for (k, v) in _json['_data'].items():
            print '{}={}'.format(k, v)
    else:
        print "Error while querying account {}: {}".format(mail, _json['_msg'])

elif action == 'create':
    # Create account in backend
    qr = backend.add_maillist(mail=mail, form=arg_kvs)
    if not qr[0]:
        print "Error while interactive with backend:", qr[1]

    r = requests.post(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print "Created."
    else:
        print "Error while creating account {}: {}".format(mail, _json['_msg'])

elif action == 'update':
    qr = backend.update_maillist(mail=mail, form=arg_kvs)
    if not qr[0]:
        print "Error while interactive with backend:", qr[1]

    r = requests.put(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print "Updated."
    else:
        print "Error while updating account {}: {}".format(mail, _json['_msg'])

elif action == 'delete':
    qr = backend.remove_maillist(mail=mail)
    if not qr[0]:
        print "Error while interactive with backend:", qr[1]

    api_url = api_url + '?' + urlencode(arg_kvs)
    r = requests.delete(api_url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        if arg_kvs.get('archive') in ['yes', None]:
            print "Removed {} (archived).".format(mail)
        else:
            print "Removed {} (without archive).".format(mail)
    else:
        print "Error while removing account {}: {}".format(mail, _json['_msg'])

elif action in ['subscribers_normal', 'subscribers_nomail', 'subscribers_digest']:
    url = api_url + '/' + action.replace('_', '/') + '?combined=yes'
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for i in _json['_data']:
            print i
    else:
        print "Error while querying account {}: {}".format(mail, _json['_msg'])
