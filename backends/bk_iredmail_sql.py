# Query SQL server on iRedMail server.
#
# Required Python modules:
#
#   - `MySQLdb` for MySQL or MariaDB backends
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

import web
from libs import utils
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
        import MySQLdb
        try:
            self.conn = self.__connect()
        except (AttributeError, MySQLdb.OperationalError):
            # Reconnect if error raised: MySQL server has gone away.
            self.conn = self.__connect()
        except Exception, e:
            logger.error("SQL error: {}".format(e))


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
        except Exception, e:
            logger.error("SQL error: {}".format(e))


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
    except Exception, e:
        # Return True as exist to not allow to create new domain/account.
        logger.error("SQL error: {}".format(e))
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

        # Check `maillists`
        qr = conn.select('maillists',
                         vars={'mail': mail},
                         what='address',
                         where='address=$mail',
                         limit=1)
        if qr:
            return True

        return False
    except Exception, e:
        logger.error("SQL error: {}".format(e))
        return True


def is_maillist_exists(mail, conn=None):
    # Return True if mailing list account is invalid or exist.
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
    except Exception, e:
        logger.error("SQL error: {}".format(e))
        return True


def add_maillist(mail, form, conn=None):
    """Add required SQL records to add a mailing list account."""
    mail = str(mail).lower()
    (_, domain) = mail.split('@', 1)

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    if not is_domain_exists(domain=domain):
        return (False, 'NO_SUCH_DOMAIN')

    if is_email_exists(mail=mail):
        return (False, 'ALREADY_EXISTS')

    name = form.get('name', '')

    try:
        conn.insert('maillists',
                    address=mail,
                    name=name,
                    domain=domain)

        logger.info('[{}] {}, created.'.format(web.ctx.ip, mail))
        return (True, )
    except Exception, e:
        logger.error('[{}] {}, error while creating: {}'.format(web.ctx.ip, mail, e))
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

        return (True, )
    except Exception, e:
        logger.error("SQL error: {}".format(e))
        return (False, repr(e))


def update_maillist(mail, form, conn=None):
    """
    Update mailing list account.

    Current only parameter `name` is stored in backend.
    """
    mail = str(mail).lower()

    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    if 'name' not in form:
        return (True, )

    if not conn:
        _wrap = SQLWrap()
        conn = _wrap.conn

    name = form.get('name', '')

    try:
        conn.update('maillists',
                    vars={'mail': mail},
                    name=name,
                    where='address=$mail')

        return (True, )
    except Exception, e:
        return (False, repr(e))
