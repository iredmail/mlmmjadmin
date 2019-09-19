# TODO list all mailing list accounts
#   - if `backend` is `bk_none`, list all accounts under mlmmj spool directory.
#   - if `backend` is not `bk_none`, query from backend.
import sys
import os
from urllib.parse import urlencode
import requests
import web
web.config.debug = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../backends')

from libs.utils import is_email
import settings

usage = """Usage:

    python3 maillist_admin.py <action> <mail> [<param1>=<value1> <param2>=<value2> ...]

Available actions:

    create: Create a new mailing list account with additional setting:
    info: Show settings of an existing mailing list account
    update: Update an existing mailing list account
    delete: Delete an existing mailing list account
    subscribers: Show all subscribers
    has_subscriber: Check whether mailing list has given subscriber.
    subscribed: Show all subscribed lists of a given subscriber.
    add_subscribers: Add new subscribers to mailing list.
    remove_subscribers: Remove existing subscribers from mailing list.

Samples:

    *) Create a new mailing list account with additional setting:

        python3 maillist_admin.py create list@domain.com only_subscriber_can_post=yes disable_archive=no

    *) Show settings of an existing mailing list account

        python3 maillist_admin.py info list@domain.com

    *) Update an existing mailing list account

        python3 maillist_admin.py update list@domain.com only_moderator_can_post=yes disable_subscription=yes

    *) Delete an existing mailing list account

        python3 maillist_admin.py delete list@domain.com

    *) Check whether mailing list has given subscriber

        python3 maillist_admin.py has_subscriber list@domain.com subscriber@gmail.com

    *) Show all subscribers:

        python3 maillist_admin.py subscribers list@domain.com

    *) Show subscribed lists of a given subscriber:

        python3 maillist_admin.py subscribed subscriber@domain.com

    *) Add new subscribers to mailing list:

        python3 maillist_admin.py add_subscribers list@domain.com <mail> <mail> <mail>

    *) Remove existing subscribers from mailing list:

        python3 maillist_admin.py remove_subscribers list@domain.com <mail> <mail> <mail>
"""

if len(sys.argv) < 3:
    print(usage)
    sys.exit()

# Base url of API interface
api_base_url = 'http://127.0.0.1:{0}/api'.format(settings.listen_port)

# Don't verify ssl cert. useful for self-signed ssl cert.
verify_ssl = False

# Use first auth token
api_auth_token = settings.api_auth_tokens[0]
api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: api_auth_token}

# Load mailing list backend.
run_backend_cli = False
if settings.backend_api == 'bk_none':
    run_backend_cli = True
    backend = __import__(settings.backend_cli)

action = sys.argv[1]
if action not in ['info', 'create', 'update', 'delete',
                  'has_subscriber',
                  'subscribers', 'subscribed',
                  'add_subscribers', 'remove_subscribers']:
    print(('<ERROR> Invalid action: {0}. Usage:'.format(action)))
    print(usage)
    sys.exit()

mail = sys.argv[2]
if not is_email(mail):
    sys.exit('Invalid email address: {0}'.format(mail))

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
        for (k, v) in list(_json['_data'].items()):
            if k in ['footer_text', 'footer_html', 'name', 'subject_prefix']:
                v = v.encode('utf-8')

            print(('{0}={1}'.format(k, v)))
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'create':
    if run_backend_cli:
        # Create account in backend
        qr = backend.add_maillist(mail=mail, form=arg_kvs)
        if not qr[0]:
            print(("Error while interactive with backend:", qr[1]))
            sys.exit()

    r = requests.post(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print("Created.")
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'update':
    if run_backend_cli:
        qr = backend.update_maillist(mail=mail, form=arg_kvs)
        if not qr[0]:
            print(("Error while interactive with backend:", qr[1]))
            sys.exit()

    r = requests.put(api_url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print("Updated.")
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'delete':
    if run_backend_cli:
        qr = backend.remove_maillist(mail=mail)
        if not qr[0]:
            print(("Error while interactive with backend:", qr[1]))
            sys.exit()

    api_url = api_url + '?' + urlencode(arg_kvs)
    r = requests.delete(api_url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        if arg_kvs.get('archive') in ['yes', None]:
            print(("Removed {0} (archived).".format(mail)))
        else:
            print(("Removed {0} (without archive).".format(mail)))
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'has_subscriber':
    _subscriber = args[0]
    url = api_url + '/has_subscriber/' + _subscriber
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print(('[YES] Mailing list <{0}> has subscriber <{1}>.'.format(mail, _subscriber)))
    else:
        if '_msg' in _json:
            print(("Error: {0}".format(_json['_msg'])))
        else:
            print(('[NO] Mailing list <{0}> does NOT have subscriber <{1}>.'.format(mail, _subscriber)))

elif action == 'subscribers':
    url = api_url + '/subscribers'
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for i in _json['_data']:
            print((i['mail'], '(%s)' % i['subscription']))
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'subscribed':
    url = api_subscriber_url + '/subscribed' + '?' + 'query_all_lists=yes'
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        for i in _json['_data']:
            print((i['mail'], '(%s)' % i['subscription']))
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'add_subscribers':
    url = api_url + '/subscribers'

    _subscribers = set([str(i).lower() for i in args if is_email(i)])
    if not _subscribers:
        print(("Error: No subscribers given."))
        sys.exit()

    arg_kvs['add_subscribers'] = ','.join(_subscribers)
    r = requests.post(url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print("Added.")
    else:
        print(("Error: {0}".format(_json['_msg'])))

elif action == 'remove_subscribers':
    url = api_url + '/subscribers'

    _subscribers = set([str(i).lower() for i in args if is_email(i)])
    if not _subscribers:
        print(("Error: No subscribers given."))
        sys.exit()

    arg_kvs['remove_subscribers'] = ','.join(_subscribers)
    r = requests.post(url, data=arg_kvs, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        print("Removed.")
    else:
        print(("Error: {0}".format(_json['_msg'])))
