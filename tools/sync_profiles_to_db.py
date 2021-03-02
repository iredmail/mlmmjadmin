#!/usr/bin/env python3
# Purpose: Sync few mailing list profiles to SQL/LDAP db, including:
#
#   - moderators (SQL table: vmail.moderators)
#   - owners (SQL table: vmail.maillist_owners)

import sys
import os
import requests
import web
web.config.debug = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../backends')

from libs.utils import is_email, is_domain, bytes2str, str2bytes
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
    import ldap
    backend = "ldap"

    from bk_iredmail_ldap import LDAPWrap
    _wrap = LDAPWrap()
    conn = _wrap.conn
else:
    print("mlmmjadmin is not configured to interactive with SQL/LDAP. Abort.")
    sys.exit()

# Available mailing lists.
mls = []

args = sys.argv[1:]
if "-A" in args:
    # Query db to get all mailing lists.
    if backend == "sql":
        qr = conn.select("maillists", what="address", where="active=1")
        for i in qr:
            addr = i["address"].lower()
            mls.append(addr)
    elif backend == "ldap":
        _filter = "(&(objectClass=mailList)(accountStatus=active)(enabledService=mlmmj))"
        try:
            qr = conn.search_s(settings.iredmail_ldap_basedn,
                               ldap.SCOPE_SUBTREE,
                               _filter,
                               ["mail"])
            for (_dn, _ldif) in qr:
                mls += [bytes2str(i).lower() for i in _ldif["mail"]]
        except Exception as e:
            print("Error while querying: {}".format(repr(e)))

    if not mls:
        print("No mailing list found. Abort.")
        sys.exit()
else:
    # Get domain names and mailing lists.
    domains = [i.lower() for i in args if is_domain(i)]
    mls = [i.lower() for i in args if is_email(i)]

    # Query SQL/LDAP to get all mailing lists under specified domains.
    if domains:
        print("Querying mailing lists under given domain(s): {}".format(", ".join(domains)))

        if backend == "sql":
            qr = conn.select("maillists",
                             vars={'domains': domains},
                             what="address",
                             where="domain IN $domains AND active=1")
            for i in qr:
                addr = i["address"].lower()
                mls.append(addr)
        elif backend == "ldap":
            for d in domains:
                _filter = "(&(objectClass=mailList)(accountStatus=active)(enabledService=mlmmj))"
                try:
                    qr = conn.search_s("domainName={},{}".format(d, settings.iredmail_ldap_basedn),
                                       ldap.SCOPE_SUBTREE,
                                       _filter,
                                       ["mail"])
                    for (_dn, _ldif) in qr:
                        mls += [bytes2str(i).lower() for i in _ldif["mail"]]
                except Exception as e:
                    print("Error while querying domain {}: {}".format(d, repr(e)))

    if not mls:
        print("No valid email address(es) of mailing lists given on command line. Abort.")
        sys.exit()

    print("Syncing {} mailing lists.".format(len(mls)))


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


def __sync_addresses(mail, addresses, address_type):
    msg = ""
    if address_type not in ["owner", "moderator"]:
        msg = "Unsupported address type: {}.".format(address_type)
        return (False, msg)

    addresses = [i.lower() for i in addresses if is_email(i)]

    if backend == "sql":
        _map = {
            "owner": {
                "table": "maillist_owners",
                "column": "owner",
            },
            "moderator": {
                "table": "moderators",
                "column": "moderator",
            },
        }
        sql_table = _map[address_type]["table"]
        sql_column = _map[address_type]["column"]

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
                msg = "Error while updating {}: {}".format(sql_table, repr(e))
                return (False, msg)

    elif backend == "ldap":
        _domain = mail.split("@", 1)[-1]
        ldn = "mail={},ou=Groups,domainName={},{}".format(mail, _domain, settings.iredmail_ldap_basedn)

        if not addresses:
            # Remove attribute.
            addresses = None

        if address_type == "owner":
            mod_attr = [(ldap.MOD_REPLACE, "listOwner", str2bytes(addresses))]
        elif address_type == "moderator":
            mod_attr = [(ldap.MOD_REPLACE, "listModerator", str2bytes(addresses))]

        try:
            conn.modify_s(ldn, mod_attr)
        except Exception as e:
            msg = "Error while updating {} of mailing list {}: {}".format(address_type, mail, repr(e))
            print("ERROR {}".format(msg))
            return (False, msg)

    return (True, )


def sync_owners(mail, owners):
    return __sync_addresses(mail=mail,
                            addresses=owners,
                            address_type="owner")


def sync_moderators(mail, moderators):
    return __sync_addresses(mail=mail,
                            addresses=moderators,
                            address_type="moderator")


for mail in mls:
    p = get_profile(mail)

    owners = p.get("owners", [])
    qr = sync_owners(mail, owners)
    if qr[0]:
        print("[OK] {}: Synced owners.".format(mail))
    else:
        print("<<< ERROR >>> {}: Failed to sync owners: {}".format(mail, qr[1]))

    moderators = p.get("moderators", [])
    qr = sync_moderators(mail, moderators)
    if qr[0]:
        print("[OK] {}: Synced moderators.".format(mail))
    else:
        print("<<< ERROR >>> {}: Failed to sync moderators: {}".format(mail, qr[1]))
