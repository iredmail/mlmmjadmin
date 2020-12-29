#!/usr/bin/env python3
# Sync few mailing list profiles to SQL/LDAP db, including:
#
#   - moderators (SQL table: vmail.moderators)
#   - members (SQL table: vmail.maillist_members)
#   - owners (SQL table: vmail.maillist_owners)

import sys
import os
import requests
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

if len(sys.argv) < 2:
    print(usage)
    sys.exit()

# Base url of API interface
api_base_url = 'http://127.0.0.1:{0}/api'.format(settings.listen_port)

# Don't verify ssl cert. useful for self-signed ssl cert.
verify_ssl = False

# Use first auth token
api_auth_token = settings.api_auth_tokens[0]
api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: api_auth_token}

# SQL/LDAP connection cursor.
conn = None
backend = None

if settings.backend_api == 'bk_iredmail_sql' or settings.backend_cli == 'bk_iredmail_sql':
    backend = "sql"

    from bk_iredmail_sql import SQLWrap
    _wrap = SQLWrap()
    conn = _wrap.conn
elif settings.backend_api == 'bk_iredmail_ldap' or settings.backend_cli == 'bk_iredmail_ldap':
    backend = "ldap"

    from bk_iredmail_ldap import LDAPWrap
    _wrap = LDAPWrap()
    conn = _wrap.conn
else:
    print("mlmmjadmin is not configured to interactive with SQL/LDAP. Abort.")
    sys.exit()

mls = []
args = sys.argv[1:]
if args[0] == '-A':
    # Query db to get all mailing lists.
    if backend == "sql":
        qr = conn.select("maillists", what="address", where="active=1")
        for i in qr:
            addr = i["address"].lower()
            mls.append(addr)
    elif backend == "ldap":
        # TODO Query LDAP
        pass

    if not mls:
        print("No mailing list found. Abort.")
        sys.exit()
else:
    # Get target MLs from command line.
    mls = [i.lower() for i in args if is_email(i)]
    if not mls:
        print("No valid email address(es) of mailing lists given on command line. Abort.")
        sys.exit()


# Get profile of mailing list.
def get_profile(mail):
    url = api_base_url + '/' + mail
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        return _json['_data']
    else:
        print("Error while getting profiles: {0}".format(_json['_msg']))


def get_member_profiles(mail):
    url = "{}/{}/subscribers".format(api_base_url, mail)
    r = requests.get(url, headers=api_headers, verify=verify_ssl)
    _json = r.json()
    if _json['_success']:
        return _json['_data']
    else:
        print("Error while getting members: {0}".format(_json['_msg']))


def sync_addresses(mail, addresses, sql_table, sql_column):
    addresses = [i.lower() for i in addresses if is_email(i)]

    if backend == "sql":
        conn.delete(sql_table,
                    vars={"mail": mail},
                    where="address=$mail")

        if addresses:
            rows = []
            for i in addresses:
                row = {
                    "address": mail,
                    sql_column: i,
                    "domain": mail.split("@", 1)[-1],
                    "dest_domain": i.split("@", 1)[-1],
                }
                rows.append(row)

            try:
                conn.multiple_insert(sql_table, rows)
            except Exception as e:
                print("Error while updating {}: {}".format(sql_table, repr(e)))
                sys.exit(255)


def sync_owners(mail, owners):
    sync_addresses(mail=mail,
                   addresses=owners,
                   sql_table="maillist_owners",
                   sql_column="owner")


def sync_moderators(mail, moderators):
    sync_addresses(mail=mail,
                   addresses=moderators,
                   sql_table="moderators",
                   sql_column="moderator")


def sync_members(mail, member_profiles):
    if backend == "sql":
        conn.delete("maillist_members",
                    vars={"mail": mail},
                    where="address=$mail")

        if member_profiles:
            rows = []
            for profile in member_profiles:
                addr = profile['mail'].lower()

                row = {
                    "address": mail,
                    "member": addr,
                    "subscription": profile['subscription'],
                    "domain": mail.split("@", 1)[-1],
                    "dest_domain": addr.split("@", 1)[-1],
                }
                rows.append(row)

            try:
                conn.multiple_insert("maillist_members", rows)
            except Exception as e:
                print("Error while updating maillist_members: {}".format(repr(e)))
                sys.exit(255)


for mail in mls:
    p = get_profile(mail)
    print("Syncing {}".format(mail))

    owners = p.get("owners", [])
    sync_owners(mail, owners)

    moderators = p.get("moderators", [])
    sync_moderators(mail, moderators)

    member_profiles = get_member_profiles(mail)
    sync_members(mail, member_profiles)
