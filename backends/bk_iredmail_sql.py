# Interactive with MySQL/MariaDB/PostgreSQL server configured by iRedMail:
# https://www.iredmail.org/
#
# For more details, please read iRedMail official tutorial:
#
#   - MySQL/MariaDB: https://docs.iredmail.org/integration.mlmmj.mysql.html
#   - PostgreSQL: https://docs.iredmail.org/integration.mlmmj.pgsql.html
#
# Required Python modules:
#
#   - `MySQL-python` for MySQL or MariaDB backends
#   - `psycopg2` for PostgreSQL backend
#
# Required parameters in settings.py
#
#   - iredmail_sql_db_type: SQL server type: mysql, pgsql.
#   - iredmail_sql_db_server: SQL server address. e.g. 127.0.0.1, localhost.
#   - iredmail_sql_db_port: SQL server port. e.g. 3306
#   - iredmail_sql_db_name: SQL database name. e.g. 'vmail'
#   - iredmail_sql_db_user: SQL username. e.g. 'vmailadmin'.
#                           Read+write privilege is required.
#   - iredmail_sql_db_password: SQL user password.

import uuid
import web
from libs import utils, form_utils
from libs.logger import logger
import settings


class MYSQLWrap(object):
    def __del__(self):
        try:
            self.conn.ctx.db.close()
        except:
            pass

    @staticmethod
    def __connect():
        conn = web.database(dbn='mysql',
                            host=settings.iredmail_sql_db_server,
                            port=int(settings.iredmail_sql_db_port),
                            db=settings.iredmail_sql_db_name,
                            user=settings.iredmail_sql_db_user,
                            pw=settings.iredmail_sql_db_password,
                            charset='utf8')

        conn.supports_multiple_insert = True

        return conn

    def __init__(self):
        try:
            self.conn = self.__connect()
        except AttributeError:  # should also catch `<db>.OperationalError`
            # Reconnect if error raised: MySQL server has gone away.
            self.conn = self.__connect()
        except Exception as e:
            logger.error("SQL error: {0}".format(e))


class PGSQLWrap(object):
    def __del__(self):
        try:
            self.conn.ctx.db.close()
        except:
            pass

    def __init__(self):
        # Initial DB connection and cursor.
        try:
            self.conn = web.database(dbn='postgres',
                                     host=settings.iredmail_sql_db_server,
                                     port=int(settings.iredmail_sql_db_port),
                                     db=settings.iredmail_sql_db_name,
                                     user=settings.iredmail_sql_db_user,
                                     pw=settings.iredmail_sql_db_password)
            self.conn.supports_multiple_insert = True
        except Exception as e:
            logger.error("SQL error: {0}".format(e))


if settings.iredmail_sql_db_type == 'mysql':
    SQLWrap = MYSQLWrap
elif settings.iredmail_sql_db_type == 'pgsql':
    SQLWrap = PGSQLWrap


def is_domain_exists(domain, conn=None):
    # Return True if account is invalid or exist.
    if not utils.is_domain(domain):
        return True

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    sql_vars = {'domain': domain}

    try:
        # Query normal mail domain
        qr = conn.select('domain',
                         vars=sql_vars,
                         what='domain',
                         where='domain=$domain',
                         limit=1)

        if qr:
            return True

        # Query alias domain
        qr = conn.select('alias_domain',
                         vars=sql_vars,
                         what='alias_domain',
                         where='alias_domain=$domain',
                         limit=1)

        if qr:
            return True

        # Domain not exist
        return False
    except Exception as e:
        # Return True as exist to not allow to create new domain/account.
        logger.error("SQL error: {0}".format(e))
        return True


def is_email_exists(mail, conn=None):
    # Return True if account is invalid or exist.
    mail = str(mail).lower()

    if not utils.is_email(mail):
        return True

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    try:
        # `forwardings` table has email addr of mail user account and alias account.
        qr = conn.select('forwardings',
                         vars={'mail': mail},
                         what='address',
                         where='address=$mail',
                         limit=1)

        if qr:
            return True

        # Check `alias` for alias account which doesn't have any member.
        qr = conn.select('alias',
                         vars={'mail': mail},
                         what='address',
                         where='address=$mail',
                         limit=1)
        if qr:
            return True

        return False
    except Exception as e:
        logger.error("SQL error: {0}".format(e))
        return True


def is_maillist_exists(mail, conn=None):
    """Return True if mailing list account is invalid or exist."""
    mail = str(mail).lower()

    if not utils.is_email(mail):
        return True

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    try:
        # Check `maillists`
        qr = conn.select('maillists',
                         vars={'mail': mail},
                         what='address',
                         where='address=$mail',
                         limit=1)
        if qr:
            return True

        return False
    except Exception as e:
        logger.error("SQL error: {0}".format(e))
        return True


def __generate_mlid():
    """Generate an server-wide unique uuid as mailing list id."""
    return str(uuid.uuid4())


def __is_mlid_exists(mlid, conn=None):
    """Return True if mailing list id exists."""
    mlid = str(mlid).lower()

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    try:
        qr = conn.select('maillists',
                         vars={'mlid': mlid},
                         what='mlid',
                         where='mlid=$mlid',
                         limit=1)
        if qr:
            return True
        else:
            return False
    except:
        return False


def __get_new_mlid(conn=None):
    mlid = __generate_mlid()

    if not conn:
        _wrap = SQLWrap()
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


def add_maillist(mail, form, conn=None):
    """Add required SQL records to add a mailing list account."""
    mail = str(mail).lower()
    (listname, domain) = mail.split('@', 1)

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    if not is_domain_exists(domain=domain):
        return (False, 'NO_SUCH_DOMAIN')

    if is_email_exists(mail=mail):
        return (False, 'ALREADY_EXISTS')

    params = {
        'active': 1,
        'address': mail,
        'domain': domain,
        'name': form.get('name', ''),
        'transport': '%s:%s/%s' % (settings.MTA_TRANSPORT_NAME, domain, listname),
        'mlid': __get_new_mlid(conn=conn),
        'maxmsgsize': form_utils.get_max_message_size(form),
    }

    if 'only_moderator_can_post' in form:
        params['accesspolicy'] = 'moderatorsonly'
    elif 'only_subscriber_can_post' in form:
        params['accesspolicy'] = 'membersonly'

    try:
        conn.insert('maillists', **params)

        params = {
            'active': 1,
            'address': mail,
            'domain': domain,
            'forwarding': mail,
            'dest_domain': domain,
        }

        conn.insert('forwardings', **params)

        # Get moderators, store in SQL table `vmail.moderators`
        if 'moderators' in form:
            moderators = [i.strip() for i in form.get('moderators', '').split(',')]
            moderators = [i.lower() for i in moderators if utils.is_email(i)]

            conn.delete('moderators',
                        vars={'address': mail},
                        where='address=$address')

            if moderators:
                records = []
                for _addr in moderators:
                    params = {
                        'address': mail,
                        'domain': domain,
                        'moderator': _addr,
                        'dest_domain': _addr.split('@', 1)[-1],
                    }

                    records.append(params)

                conn.multiple_insert('moderators', records)

        logger.info('Created: {0}.'.format(mail))
        return (True,)
    except Exception as e:
        logger.error('Error while creating {0}: {1}'.format(mail, e))
        return (False, repr(e))


def remove_maillist(mail, conn=None):
    """Remove required SQL records to remove a mailing list account."""
    mail = str(mail).lower()

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    try:
        conn.delete('maillists',
                    vars={'mail': mail},
                    where='address=$mail')

        conn.delete('forwardings',
                    vars={'mail': mail},
                    where='address=$mail')

        return (True,)
    except Exception as e:
        logger.error("SQL error: {0}".format(e))
        return (False, repr(e))


def update_maillist(mail, form, conn=None):
    """
    Update mailing list account.

    Parameters stored in backend:

    - name
    - moderators
    - only_moderator_can_post
    - only_subscriber_can_post
    """
    mail = str(mail).lower()
    domain = mail.split('@', 1)[-1]

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    params = {
        'name': form.get('name', ''),
    }

    if 'max_message_size' in form:
        params['maxmsgsize'] = form_utils.get_max_message_size(form)

    if 'only_moderator_can_post' in form:
        params['accesspolicy'] = 'moderatorsonly'
    elif 'only_subscriber_can_post' in form:
        params['accesspolicy'] = 'membersonly'

    try:
        conn.update('maillists',
                    vars={'mail': mail},
                    where='address=$mail',
                    **params)

        # Get moderators, store in SQL table `vmail.moderators`
        if 'moderators' in form:
            moderators = [i.strip() for i in form.get('moderators', '').split(',')]
            moderators = [i.lower() for i in moderators if utils.is_email(i)]

            conn.delete('moderators',
                        vars={'address': mail},
                        where='address=$address')

            if moderators:
                records = []
                for _addr in moderators:
                    params = {
                        'address': mail,
                        'domain': domain,
                        'moderator': _addr,
                        'dest_domain': _addr.split('@', 1)[-1],
                    }

                    records.append(params)

                conn.multiple_insert('moderators', records)

        return (True,)
    except Exception as e:
        return (False, repr(e))


def get_existing_maillists(domains=None, conn=None):
    """Get existing mailing lists.

    :param domains: a list/tuple/set of valid domain names.
                    Used if you want to get mailing lists under given domains.
    :param conn: sql connection cursor.
    """
    if domains:
        domains = [str(d).lower() for d in domains if utils.is_domain(d)]

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    existing_lists = set()
    try:
        if domains:
            qr = conn.select('maillists',
                             vars={'domains': domains},
                             what='address',
                             where='domain IN $domains',
                             group='address')
        else:
            qr = conn.select('maillists',
                             what='address',
                             group='address')

        for i in qr:
            _addr = str(i.address).lower()
            existing_lists.add(_addr)

        return (True, list(existing_lists))
    except Exception as e:
        return (False, repr(e))
