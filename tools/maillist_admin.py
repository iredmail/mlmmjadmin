# TODO list all mailing list accounts
#   - if `backend` is `bk_none`, list all accounts under mlmmj spool directory.
#   - if `backend` is not `bk_none`, query from backend.
import sys
import os
from urllib import urlencode
import requests
import web
web.config.debug = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../backends')

from libs.utils import is_email
import settings

usage = """Usage:

    python maillist_admin.py <action> <mail> [<param1>=<value1> <param2>=<value2> ...]

Valid actions:

    create: Create a new mailing list account with additional setting:
    info: Show settings of an existing mailing list account
    update: Update an existing mailing list account
    delete: Delete an existing mailing list account
    has_subscriber: Check whether mailing list has given subscriber.
    subscribers: Show all subscribers
    subscribed: Show all subscribed lists of a given subscriber.

To subscribe/unsubscribe address to/from a mailing list, please run command
`mlmmj-sub` and `mlmmj-unsub` shipped in mlmmj package instead.

Samples:

    *) Create a new mailing list account with additional setting:

        python maillist_admin.py create list@domain.com only_subscriber_can_post=yes disable_archive=no

    *) Show settings of an existing mailing list account

        python maillist_admin.py info list@domain.com

    *) Update an existing mailing list account

        python maillist_admin.py update list@domain.com only_moderator_can_post=yes disable_subscription=yes

    *) Delete an existing mailing list account

        python maillist_admin.py delete list@domain.com

    *) Check whether mailing list has given subscriber.

        python maillist_admin.py has_subscriber list@domain.com subscriber@gmail.com

    *) Show all subscribers:

        python maillist_admin.py subscribers list@domain.com

    *) Show subscribed lists of a given subscriber:

        python maillist_admin.py subscribed subscriber@domain.com
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
                  'has_subscriber',
                  'subscribers', 'subscribed']:
    print '<ERROR> Invalid action: {}. Usage:'
    print usage
    sys.exit()

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
api_subscriber_url = api_base_url + '/subscriber/' + mail

if action == 'info':
    r = requests.get(api_url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for (k, v) in _json['_data'].items():
            print '{}={}'.format(k, v)
    else:
        print "Error: {}".format(_json['_msg'])

elif action == 'create':
    # Create account in backend
    qr = backend.add_maillist(mail=mail, form=arg_kvs)
    if not qr[0]:
        print "Error while interactive with backend:", qr[1]
        sys.exit()

    r = requests.post(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print "Created."
    else:
        print "Error: {}".format(_json['_msg'])

elif action == 'update':
    qr = backend.update_maillist(mail=mail, form=arg_kvs)
    if not qr[0]:
        print "Error while interactive with backend:", qr[1]
        sys.exit()

    r = requests.put(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print "Updated."
    else:
        print "Error: {}".format(_json['_msg'])

elif action == 'delete':
    qr = backend.remove_maillist(mail=mail)
    if not qr[0]:
        print "Error while interactive with backend:", qr[1]
        sys.exit()

    api_url = api_url + '?' + urlencode(arg_kvs)
    r = requests.delete(api_url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        if arg_kvs.get('archive') in ['yes', None]:
            print "Removed {} (archived).".format(mail)
        else:
            print "Removed {} (without archive).".format(mail)
    else:
        print "Error: {}".format(_json['_msg'])

elif action == 'has_subscriber':
    _subscriber = args[0]
    url = api_url + '/has_subscriber/' + _subscriber
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print '[YES] Mailing list <{}> has subscriber <{}>.'.format(mail, _subscriber)
    else:
        if '_msg' in _json:
            print "Error: {}".format(_json['_msg'])
        else:
            print '[NO] Mailing list <{}> does NOT have subscriber <{}>.'.format(mail, _subscriber)

elif action == 'subscribers':
    url = api_url + '/subscribers'
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for i in _json['_data']:
            print i['mail'], '(%s)' % i['subscription']
    else:
        print "Error: {}".format(_json['_msg'])

elif action == 'subscribed':
    url = api_subscriber_url + '/subscribed' + '?' + 'query_all_lists=yes'
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for i in _json['_data']:
            print i['mail'], '(%s)' % i['subscription']
    else:
        print "Error: {}".format(_json['_msg'])
