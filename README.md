# Mlmmj Admin

mlmmj-admin is RESTful API server used to manage mlmmj (mailing list manager).
Check `docs/` directory for more detailed documents.

* [90% DONE] RESTful API interface for managing mlmmj mailing list accounts
* [Not started] web interface to allow moderators and end users to manage
  their own subscriptions.

## Requirements

* A working mail server with a working mlmmj instance.
    * For iRedMail users, please follow tutorial `docs/integration-iredmail-*.md`
      to integrate mlmmj.
    * Mlmmj data will be stored under `/var/spool/mlmmj`, it must be owned by
      user/group `mlmmj:mlmmj` with permission 0700. if you want to change it,
      please override it with setting `MLMMJ_SPOOL_DIR =` in its config file.
* Python 2.6.x or 2.7.x, with extra modules:
    * `web.py
    * `requests`: required by `tools/maillist_admin.py`.

## Setup mlmmj-admin

> Please follow docs under `docs/` directory to integrate mlmmj first, make
> sure it's working properly.

* Create directory used to store mlmmj-admin program:

```
mkdir -p /opt/mlmmj-admin
```

* Copy files to `/opt/mlmmj-admin`.
* Copy systemd service file (a SysV script is available too):

```
cp /opt/mlmmj-admin/rc_scripts/mlmmjadmin.service /lib/systemd/system
systemctl enable mlmmjadmin
```

* Generate a config file by copying `settings.py.sample`:

```
cd /opt/mlmmj-admin/
cp settings.py.sample settings.py
chown mlmmj:mlmmj settings.py
chmod 0400 settings.py
```

* Generate a long string as API auth token, it will be used by your API client.
  For example:

```
$ echo $RANDOM | md5
43a89b7aa34354089e629ed9f9be0b3b
```

* Add this API auth token in config file `settings.py`, parameter `api_auth_tokens`. For example:

```
api_auth_tokens = ['43a89b7aa34354089e629ed9f9be0b3b']
```

You can add as many token as you want by different API clients.

* Choose a proper mailing list backend and add required parameters.

    * If you set `backend` to `bk_none` in config file, no addition
      config required. Other backend may requires additional parameters.
    * For iRedMail users:
        - Backend `bk_iredmail_sql` requires few parameters to connect to
          `vmail` database on iRedMail server, please open file
          `backends/bk_iredmail_sql.py` to find the required parameters in
          the comment lines.
        - [TODO] Backend `bk_iredmail_ldap`

* Create directory used to store mlmmj-admin log file:

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

* Update syslog config file to log mlmmj-admin to dedicated log file:

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

## Tips

mlmmj will log its operaions in 2 files under mailing list directory:

* `mlmmj.operation.log`: mlmmj logs mail sending, rejecting, subscription, etc
  in this file.
* `mlmmj-maintd.lastrun.log`: mlmmj logs maintenance related task info in this file.
