import sys
import os
from urllib import urlencode
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from tools import api_headers, api_base_url
from libs.utils import is_email

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
    r = requests.get(api_url, headers=api_headers, verify=False)

elif action == 'create':
    r = requests.post(api_url, data=args, headers=api_headers, verify=False)
    _json = r.json()
    if _json['_success']:
        print "Created."
    else:
        print "Error while creating account {}: {}".format(mail, _json['_msg'])

elif action == 'update':
    pass

elif action == 'delete':
    api_url = api_url + '?' + urlencode(arg_kvs)
    r = requests.delete(api_url, data=args, headers=api_headers, verify=False)
    _json = r.json()
    if _json['_success']:
        if args.get('archive') == 'yes':
            print "Removed {} (archived).".format(mail)
        else:
            print "Removed {} (without archive).".format(mail)
    else:
        print "Error while removing account {}: {}".format(mail, _json['_msg'])
