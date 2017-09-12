import sys
import os
from urllib import urlencode
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from libs.utils import is_email
import settings

usage = """Usage:

    python maillist_manage.py <info|create|update|delete> <mail> [<param1>=<value1> <param2>=<value2> ...]

Samples:

    *) Get settings of an existing mailing list account

        python maillist_manage.py info listname@domain.com

    *) Create a new mailing list account with additional setting:

        python maillist_manage.py create listname@domain.com only_subscriber_can_post=yes disable_archive=no

    *) Update an existing mailing list account

        python maillist_manage.py update listname@domain.com only_moderator_can_post=yes disable_subscription=yes

    *) Delete an existing mailing list account

        python maillist_manage.py delete listname@domain.com archive=yes
"""

# Base url of API interface
api_base_url = 'http://127.0.0.1:{}/api'.format(settings.listen_port)

# Don't verify ssl cert. useful for self-signed ssl cert.
verify_ssl = False

# Use first auth token
api_auth_token = settings.api_auth_tokens[0]
api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: api_auth_token}

action = sys.argv[1]
if action not in ['info', 'create', 'update', 'delete']:
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
    r = requests.post(api_url, data=args, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print "Created."
    else:
        print "Error while creating account {}: {}".format(mail, _json['_msg'])

elif action == 'update':
    r = requests.put(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print "Updated."
    else:
        print "Error while updating account {}: {}".format(mail, _json['_msg'])

elif action == 'delete':
    api_url = api_url + '?' + urlencode(arg_kvs)
    r = requests.delete(api_url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        if arg_kvs.get('archive') == 'yes':
            print "Removed {} (archived).".format(mail)
        else:
            print "Removed {} (without archive).".format(mail)
    else:
        print "Error while removing account {}: {}".format(mail, _json['_msg'])
