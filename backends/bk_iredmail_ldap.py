# Query LDAP server on iRedMail server.
#
# Required Python modules:
#
#   - `python-ldap` for LDAP backends
#
# Required parameters in settings.py
#
#   - iredmail_ldap_uri: LDAP server uri. Examples:
#       - 'ldap://127.0.0.1': normal LDAP connection (port 389)
#       - 'ldaps://127.0.0.1': secure connection through STARTTLS (port 389)
#
#   - iredmail_ldap_basedn: dn which contains all mail domains and accounts.
#   - iredmail_ldap_bind_dn: the bind dn used to update LDAP data.
#   - iredmail_ldap_bind_password: password of bind dn in plain text.

import uuid
import ldap
import web

from libs import utils
from libs.logger import logger
import settings


class LDAPWrap(object):
    def __init__(self):
        # Initialize LDAP connection.
        self.conn = None

        uri = settings.iredmail_ldap_uri

        # Detect STARTTLS support.
        starttls = False
        if uri.startswith('ldaps://'):
            starttls = True

            # Rebuild uri, use ldap:// + STARTTLS (with normal port 389)
            # instead of ldaps:// (port 636) for secure connection.
            uri = uri.replace('ldaps://', 'ldap://')

            # Don't check CA cert
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        self.conn = ldap.initialize(uri)

        # Set LDAP protocol version: LDAP v3.
        self.conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)

        if starttls:
            self.conn.start_tls_s()

        try:
            # bind as vmailadmin
            self.conn.bind_s(settings.iredmail_ldap_bind_dn, settings.iredmail_ldap_bind_password)
        except Exception, e:
            web.log_error('VMAILADMIN_INVALID_CREDENTIALS. Detail: %s' % repr(e))

    def __del__(self):
        try:
            if self.conn:
                self.conn.unbind()
        except:
            pass


# Check whether domain name (either primary domain or alias domain) exists
def is_domain_exists(domain, conn=None):
    # Return True if account is invalid or exist.
    domain = str(domain).strip().lower()

    if not utils.is_domain(domain):
        # Return False if invalid.
        return False

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    query_filter = '(&'
    query_filter += '(objectClass=mailDomain)'
    query_filter += '(|(domainName=%s)(domainAliasName=%s))' % (domain, domain)
    query_filter += ')'

    # Check domainName and domainAliasName.
    try:
        qr = conn.search_s(settings.iredmail_ldap_basedn,
                           ldap.SCOPE_ONELEVEL,
                           query_filter,
                           ['dn'])

        if qr:
            # Domain name exist.
            return True
        else:
            return False
    except:
        # Account 'EXISTS' (fake) if lookup failed.
        return True

# Check whether account exist or not.
# Return True if account is invalid or exist.
def is_email_exists(mail, conn=None):
    mail = str(mail).lower()
    mail = utils.strip_mail_ext_address(mail)

    if not utils.is_email(mail):
        return True

    # Filter used to search mail accounts.
    query_filter = '(&'
    query_filter += '(|(objectClass=mailUser)(objectClass=mailList)(objectClass=mailingList)(objectClass=mailAlias))'
    query_filter += '(|(mail=%s)(shadowAddress=%s))' % (mail, mail)
    query_filter += ')'

    try:
        if not conn:
            _wrap = LDAPWrap()
            conn = _wrap.conn

        qr = conn.search_s(settings.iredmail_ldap_basedn,
                           ldap.SCOPE_SUBTREE,
                           query_filter,
                           ['dn'])

        if qr:
            return True
        else:
            # Account not exist.
            return False
    except:
        # Account 'EXISTS' (fake) if lookup failed.
        return True


def is_maillist_exists(mail, conn=None):
    """Check whether mailing list account exists."""
    mail = str(mail).lower()
    if not utils.is_email(mail):
        return True

    # Filter used to search mail accounts.
    query_filter = '(&'
    query_filter += '(|(objectClass=mailUser)(objectClass=mailList)(objectClass=mailAlias))'
    query_filter += '(|(mail=%s)(shadowAddress=%s))' % (mail, mail)
    query_filter += ')'

    try:
        if not conn:
            _wrap = LDAPWrap()
            conn = _wrap.conn

        qr = conn.search_s(settings.iredmail_ldap_basedn,
                           ldap.SCOPE_SUBTREE,
                           query_filter,
                           ['dn'])

        if qr:
            return True
        else:
            # Account not exist.
            return False
    except:
        return False


def __generate_mlid():
    """Generate an server-wide unique uuid as mailing list id."""
    return str(uuid.uuid4())

def __is_mlid_exists(mlid, conn=None):
    """Return True if mailing list id exists."""
    mlid = str(mlid).lower()

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    try:
        qr = conn.search_s(settings.iredmail_ldap_basedn,
                           ldap.SCOPE_SUBTREE,
                           '(&(objectClass=mailList)(enabledService=mlmmj)(mailingListID=%s))' % mlid,
                           ['dn'])

        if qr:
            return True
        else:
            return False
    except:
        return False


def __get_new_mlid(conn=None):
    mlid = __generate_mlid()

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    _counter = 0
    while True:
        # Try 20 times.
        if _counter >= 20:
            raise ValueError("Cannot get an unique mailing list id after tried 20 times.")

        if not __is_mlid_exists(mlid=mlid, conn=conn):
            break
        else:
            _counter += 1
            mlid = __generate_mlid()

    return mlid

def __ldif_ml(mail,
              mlid,
              name=None,
              access_policy=None,
              alias_domains=None,
              domain_status=None):
    """Generate LDIF (a dict) for a new (mlmmj) mailing list account.

    :param mail: mail address of new (mlmmj) mailing list account
    :param mlid: a server-wide unique id for each (mlmmj) mailing list
    :param name: short description of mailing list
    :param access_policy: access policy of mailing list
    :param alias_domains: a list/tuple/set of alias domains
    :param domain_status: status of primary domain: active, disabled.
    """
    mail = str(mail).lower()
    listname, domain = mail.split('@', 1)
    transport = '%s:%s/%s' % (settings.MTA_TRANSPORT_NAME, domain, listname)

    ldif = [('objectClass', ['mailList']),
            ('accountStatus', ['active']),
            ('enabledService', ['mail', 'deliver', 'mlmmj']),
            ('mtaTransport', [transport]),
            ('mail', [mail]),
            ('mailingListID', [mlid])]

    if name:
        ldif += [('cn', [name.encode('utf-8')])]

    if alias_domains:
        alias_domains = [str(d).lower() for d in alias_domains if utils.is_domain(d)]
        shadow_addresses = [listname + '@' + d for d in alias_domains]

        if shadow_addresses:
            ldif += [('shadowAddress', shadow_addresses)]

    if domain_status != 'active':
        ldif += [('domainStatus', ['disabled'])]

    return ldif

def __add_or_remove_attr_value(dn, attr, value, action, conn=None):
    """Add or remove value of attribute which can handle multiple values.

    :param attr: ldap attribute name we need to update
    :param value: value of attribute name
    :param action: to add value, use one of: add, assign, enable.
                   to delete value, use one of: del, delete, remove, disable
    :param conn: ldap connection cursor
    """
    if isinstance(value, list):
        values = value
    else:
        values = [value]

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    msg = ''
    if action in ['add', 'assign', 'enable']:
        for v in values:
            try:
                conn.modify_s(dn, [(ldap.MOD_ADD, attr, str(v))])
            except (ldap.NO_SUCH_OBJECT, ldap.TYPE_OR_VALUE_EXISTS):
                pass
            except Exception, e:
                msg += str(e)
    elif action in ['del', 'delete', 'remove', 'disable']:
        for v in values:
            try:
                conn.modify_s(dn, [(ldap.MOD_DELETE, attr, str(v))])
            except ldap.NO_SUCH_ATTRIBUTE:
                pass
            except Exception, e:
                msg += str(e)
    else:
        return (False, 'UNKNOWN_ACTION')

    if not msg:
        return (True, )
    else:
        return (False, msg)


def __get_primary_and_alias_domains(domain, with_primary_domain=True, conn=None):
    '''Get list of domainName and domainAliasName by quering domainName.

    >>> get_primary_and_alias_domains(domain='example.com')
    (True, ['example.com', 'aliasdomain01.com', 'aliasdomain02.com', ...])
    '''
    domain = web.safestr(domain).strip().lower()
    if not utils.is_domain(domain):
        return (False, 'INVALID_DOMAIN_NAME')

    try:
        if not conn:
            _wrap = LDAPWrap()
            conn = _wrap.conn

        dn = 'domainName=%s,%s' % (domain, settings.iredmail_ldap_basedn)
        qr = conn.search_s(dn,
                           ldap.SCOPE_BASE,
                           '(&(objectClass=mailDomain)(domainName=%s))' % domain,
                           ['domainName', 'domainAliasName'])

        if qr:
            all_domains = qr[0][1].get('domainName', []) + qr[0][1].get('domainAliasName', [])
            if not with_primary_domain:
                all_domains.remove(domain)
            return (True, all_domains)
        else:
            return (False, 'INVALID_DOMAIN_NAME')
    except Exception, e:
        return (False, repr(e))


def add_maillist(mail, form, conn=None):
    """Add required LDAP object to add a mailing list account."""
    mail = str(mail).lower()
    (_, domain) = mail.split('@', 1)

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    if not is_domain_exists(domain=domain):
        return (False, 'NO_SUCH_DOMAIN')

    if is_email_exists(mail=mail):
        return (False, 'ALREADY_EXISTS')

    name = form.get('name', '')
    mlid = __get_new_mlid(conn=conn)

    domain_status = 'disabled'
    alias_domains = []

    dn_domain = 'domainName=%s,%s' % (domain, settings.iredmail_ldap_basedn)
    # Get domain profile.
    try:
        qr = conn.search_s(dn_domain,
                           ldap.SCOPE_BASE,
                           '(objectClass=*)')

        if qr:
            _ldif = qr[0][1]
            domain_status = _ldif.get('accountStatus', ['disabled'])[0]

            alias_domains = _ldif.get('domainAliasName', [])
            alias_domains = [str(i).lower() for i in alias_domains if utils.is_domain(i)]
            alias_domains = list(set(alias_domains))

        dn_ml = 'mail=%s,ou=Groups,domainName=%s,%s' % (mail, domain, settings.iredmail_ldap_basedn)
        ldif_ml = __ldif_ml(mail=mail,
                            mlid=mlid,
                            name=name,
                            alias_domains=alias_domains,
                            domain_status=domain_status)

        conn.add_s(dn_ml, ldif_ml)
        logger.info('Created: {}.'.format(mail))
        return (True, )
    except Exception, e:
        logger.error('Error while creating {}: {}'.format(mail, e))
        return (False, repr(e))


def remove_maillist(mail, conn=None):
    """Remove LDAP object to remove a mailing list account."""
    mail = str(mail).lower()
    (_, domain) = mail.split('@', 1)

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    try:
        dn = 'mail=%s,ou=Groups,domainName=%s,%s' % (mail, domain, settings.iredmail_ldap_basedn)
        conn.delete_s(dn)
        return (True, )
    except Exception, e:
        logger.error("Error: {}".format(e))
        return (False, repr(e))


def update_maillist(mail, form, conn=None):
    """Update mailing list account.

    Parameters stored in backend:

    @name
    """
    mail = str(mail).lower()
    (_, domain) = mail.split('@', 1)

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if 'name' not in form:
        return (True, )

    if not conn:
        _wrap = LDAPWrap()
        conn = _wrap.conn

    name = form.get('name', '')

    try:
        dn = 'mail=%s,ou=Groups,domainName=%s,%s' % (mail, domain, settings.iredmail_ldap_basedn)

        if name:
            __add_or_remove_attr_value(dn, attr='cn', value=name, action='add', conn=conn)
        else:
            # Remove 'cn'.
            conn.modify_s(dn, [(ldap.MOD_REPLACE, 'cn', None)])

        return (True, )
    except Exception, e:
        return (False, repr(e))
