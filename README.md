# Mlmmj Admin

mlmmj-admin is RESTful API server used to manage mlmmj (mailing list manager).
Check `docs/` directory for more detailed documents.

## Requirements

* A working mail server with a working mlmmj instance.
    * Mlmmj data is configured to be stored under `/var/spool/mlmmj` by
      default, it must be owned by user/group `mlmmj:mlmmj` with permission
      `0700`. if you use a different directory, please override default setting
      by adding setting `MLMMJ_SPOOL_DIR = '<directory>'` in config file.
* Python 2.6.x or 2.7.x, with extra modules:
    * `web.py`: <http://webpy.org/>
    * `requests`: <http://docs.python-requests.org/en/master/>. Required by
      command line tool `tools/maillist_admin.py`.

## Setup mlmmj-admin

> Please follow docs under `docs/` directory to integrate mlmmj first, make
> sure it's working properly.

NOTE: We use version `1.0` for example below.

* Download mlmmj-admin: <https://bitbucket.org/iredmail/mlmmj-admin/downloads/>
* Uncompress downloaded mlmmj-admin package, copy it to `/opt/` directory.
* Create symbol link:

```
cd /opt
ln -s mlmmj-admin-1.0 mlmmj-admin
```

* Generate config file by copying sample file, `settings.py.sample`:

```
cp settings.py.sample settings.py
chown mlmmj:mlmmj settings.py
chmod 0400 settings.py
```

* Open `settings.py`, make sure all settings are proper. The config file is
  short, please spend few seconds to read all parameters and the comment lines.
* Generate a long string as API auth token, it will be used by your API client.
  For example:

```
$ echo $RANDOM | md5sum
43a89b7aa34354089e629ed9f9be0b3b
```

* Add this string in config file `settings.py`, parameter `api_auth_tokens`,
  like below:

```
api_auth_tokens = ['43a89b7aa34354089e629ed9f9be0b3b']
```

You can add as many token as you want for different API clients. For example:

```
api_auth_tokens = ['43a89b7aa34354089e629ed9f9be0b3b', '703ed37b20243d7c51c56ce6cd90e94c']
```

* If you're running iRedMail as your mail server, please update parameters
  `backend_api` and `backend_cli` to use a proper backend handler. The backend
  handler will connect to SQL/LDAP server to sync data of mlmmj mailing list.
    * if you manage mail accounts with iRedAdmin-Pro:
        * Please set `backend_api = 'bk_none'`
        * if you're running SQL backends, please set
          `backend_api = 'bk_iredmail_sql'` in `settings.py`.
        * if you're running LDAP backends, please set
          `backend_api = 'bk_iredmail_ldap'` in `settings.py`.
    * if you do not manage mail accounts with iRedAdmin-Pro:
        * if you're running SQL backends, please set
          `backend_api = 'bk_iredmail_sql'` and
          `backend_cli = 'bk_iredmail_sql'` in `settings.py`.
        * if you're running LDAP backends, please set
          `backend_api = 'bk_iredmail_ldap'` and
          `backend_cli = 'bk_iredmail_ldap` in `settings.py`.
    * Please add extra __REQUIRED__ parameters in `settings.py`, so that
      mlmmj-admin can connect and update LDAP server. Parameters are explanned
      in file `backends/bk_iredmail_<backend>.py`.

```
#
# For SQL backends
#
iredmail_sql_db_type = 'mysql'          # or 'pgsql' for PostgreSQL
iredmail_sql_db_server = '127.0.0.1'
iredmail_sql_db_port = 3306             # or 5432 for PostgreSQL
iredmail_sql_db_name = 'vmail'
iredmail_sql_db_user = 'vmailadmin'     # SQL user must have read+write
                                        # privilege to access 'vmail' database
iredmail_sql_db_password = 'xxxxxxxx'   # Password of `iredmail_sql_db_user`

#
# For LDAP backends
#
iredmail_ldap_uri = 'ldap://127.0.0.1'
iredmail_ldap_basedn = 'o=domains,dc=XXX,dc=XXX'
iredmail_ldap_bind_dn = 'cn=vmailadmin,dc=XXX,dc=XXX'
iredmail_ldap_bind_password = 'xxxxxxxx'
```

* Create directory used to store mlmmj-admin log file. mlmmj-admin is
  configured to log to syslog directly.

```
#
# For RHEL/CentOS
#
mkdir /var/log/mlmmj-admin
chown root:root /var/log/mlmmj-admin
chmod 0755 /var/log/mlmmj-admin

#
# For Debian/Ubuntu
#
mkdir /var/log/mlmmj-admin
chown syslog:adm /var/log/mlmmj-admin
chmod 0755 /var/log/mlmmj-admin

#
# For OpenBSD/FreeBSD
#
mkdir /var/log/mlmmj-admin
chown root:wheel /var/log/mlmmj-admin
chmod 0755 /var/log/mlmmj-admin
```

* Update syslog daemon config file to log mlmmj-admin to dedicated log file:

For Linux
```
cp /opt/mlmmj-admin/samples/rsyslog/mlmmj-admin.conf /etc/rsyslog.d/
service rsyslog restart
```

For OpenBSD, please append below lines in `/etc/syslog.conf`:

```
!!mlmmj-admin
local5.*            /var/log/mlmmj-admin/mlmmj-admin.log
```

---
[TODO] For FreeBSD
---

* [TODO] Copy systemd or rc script used to control mlmmj-admin service:

* Now ok to start `mlmmjadmin` service:

```
service mlmmjadmin restart
```

## Interactive with curl

```
# Create a new mailing list
curl \
    -X POST \
    --header 'X-MLMMJ-ADMIN-API-AUTH-TOKEN: 43a89b7aa34354089e629ed9f9be0b3b' \
    -d "owner=postmaster@a.io&only_subscriber_can_post=yes"
    http://127.0.0.1:7779/list@domain.com

# Update a mailing list
curl \
    -X PUT \
    --header 'X-MLMMJ-ADMIN-API-AUTH-TOKEN: 43a89b7aa34354089e629ed9f9be0b3b' \
    -d "only_subscriber_can_post=no"
    http://127.0.0.1:7779/list@domain.com

# Delete a mailing list
curl \
    -X DELETE \
    --header 'X-MLMMJ-ADMIN-API-AUTH-TOKEN: 43a89b7aa34354089e629ed9f9be0b3b' \
    http://127.0.0.1:7779/list@domain.com
```

## Manage mailing lists from command line

Script `tools/maillist_admin.py` supports basic management from command line.

* Get settings of an existing mailing list account

    ```python maillist_admin.py info list@domain.com```

* Create a new mailing list account with additional setting:

    ```python maillist_admin.py create list@domain.com only_subscriber_can_post=yes disable_archive=no```

* Update an existing mailing list account

    ```python maillist_admin.py update list@domain.com only_moderator_can_post=yes disable_subscription=yes```

* Delete an existing mailing list account

    ```python maillist_admin.py delete list@domain.com archive=yes```

* Get subscribers which subscribed to `normal` version:

    ```python maillist_admin.py subscribers_normal list@domain.com```

* Get subscribers which subscribed to `digest` version:

    ```python maillist_admin.py subscribers_digest list@domain.com```

* Get subscribers which subscribed to `nomail` version:

    ```python maillist_admin.py subscribers_nomail list@domain.com```

## Tips

mlmmj will log its operaions in 2 files under mailing list directory:

* `mlmmj.operation.log`: mlmmj logs mail sending, rejecting, subscription, etc
  in this file.
* `mlmmj-maintd.lastrun.log`: mlmmj logs maintenance related task info in this file.
