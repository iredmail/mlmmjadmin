# mlmmjadmin

mlmmjadmin is RESTful API server used to manage mlmmj (mailing list manager).
Check `docs/` directory for more detailed documents.

mlmmjadmin is a core component of iRedMail (since version 0.9.8), but it should
work with any mail server which runs mlmmj. You're free to develop your own
backend plugin to store basic info of mlmmj mailing lists in your
SQL/LDAP database (or any other database, it's up to you) for better
integration with your mail server.

## License

MIT License.

## Requirements

* A working mail server with a working mlmmj instance.
    * Mlmmj data is configured to be stored under `/var/spool/mlmmj` by
      default, it must be owned by user/group `mlmmj:mlmmj` with permission
      `0700`. if you use a different directory, please override default setting
      by adding setting `MLMMJ_SPOOL_DIR = '<directory>'` in config file.
* Python 3.5+. If you're running Python 2, please use mlmmjadmin-2.1 instead.
* Extra Python modules:
    * [web.py](http://webpy.org/)
    * [requests](http://docs.python-requests.org/en/master/). Required by
      command line tool `tools/maillist_admin.py`.

## Setup mlmmj

Please follow iRedMail tutorials to integrate mlmmj with Postfix first, make
sure it's working properly:

* [For LDAP backends](https://docs.iredmail.org/integration.mlmmj.ldap.html)
* [For MySQL/MariaDB backend](https://docs.iredmail.org/integration.mlmmj.mysql.html)
* [For PostgreSQL backend](https://docs.iredmail.org/integration.mlmmj.pgsql.html)

## Setup mlmmjadmin

NOTE: We use version `3.0` for example below.

* Download the latest mlmmjadmin: <https://github.com/iredmail/mlmmjadmin/releases>
* Uncompress downloaded mlmmjadmin package, copy it to `/opt/` directory.
* Create symbol link:

```
cd /opt
ln -s mlmmjadmin-3.0 mlmmjadmin
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

* Copy rc/systemd scripts for service control:

```
#
# For RHEL/CentOS
#
cp /opt/mlmmjadmin/rc_scripts/systemd/rhel.service /lib/systemd/system/mlmmjadmin.service
chmod 0644 /lib/systemd/system/mlmmjadmin.service
systemctl daemon-reload
systemctl enable mlmmjadmin

#
# For Debian 9 and Ubuntu 16.04 which systemd
#
cp /opt/mlmmjadmin/rc_scripts/systemd/debian.service /lib/systemd/system/mlmmjadmin.service
chmod 0644 /lib/systemd/system/mlmmjadmin.service
systemctl daemon-reload
systemctl enable mlmmjadmin

#
# For FreeBSD
#
cp /opt/mlmmjadmin/rc_scripts/mlmmjadmin.freebsd /usr/local/etc/rc.d/mlmmjadmin
echo 'mlmmjadmin_enable=YES' >> /etc/rc.conf.local

#
# For OpenBSD
#
cp /opt/mlmmjadmin/rc_scripts/mlmmjadmin.openbsd /etc/rc.d/mlmmjadmin
chmod 0755 /etc/rc.d/mlmmjadmin
rcctl enable mlmmjadmin
```


* Create directory used to store mlmmjadmin log file. mlmmjadmin is
  configured to log to syslog directly.

```
#
# For RHEL/CentOS
#
mkdir /var/log/mlmmjadmin
chown root:root /var/log/mlmmjadmin
chmod 0755 /var/log/mlmmjadmin

#
# For Debian/Ubuntu
#
mkdir /var/log/mlmmjadmin
chown syslog:adm /var/log/mlmmjadmin
chmod 0755 /var/log/mlmmjadmin

#
# For OpenBSD/FreeBSD
#
mkdir /var/log/mlmmjadmin
chown root:wheel /var/log/mlmmjadmin
chmod 0755 /var/log/mlmmjadmin
```

* Update syslog daemon config file to log mlmmjadmin to dedicated log file:

For Linux
```
cp /opt/mlmmjadmin/samples/rsyslog/mlmmjadmin.conf /etc/rsyslog.d/
service rsyslog restart
```

For OpenBSD, please append below lines in `/etc/syslog.conf`:

```
!!mlmmjadmin
local5.*            /var/log/mlmmjadmin/mlmmjadmin.log
```

For FreeBSD, please append below lines in `/etc/

```
!mlmmjadmin
local5.*            /var/log/mlmmjadmin/mlmmjadmin.log
```

* Now ok to start `mlmmjadmin` service:

```
service mlmmjadmin restart
```

## Interactive with curl

```
# Create a new mailing list
curl \
    -X POST \
    --header 'X-MLMMJADMIN-API-AUTH-TOKEN: 43a89b7aa34354089e629ed9f9be0b3b' \
    -d "owner=postmaster@a.io&only_subscriber_can_post=yes"
    http://127.0.0.1:7790/list@domain.com

# Update a mailing list
curl \
    -X PUT \
    --header 'X-MLMMJADMIN-API-AUTH-TOKEN: 43a89b7aa34354089e629ed9f9be0b3b' \
    -d "only_subscriber_can_post=no"
    http://127.0.0.1:7790/list@domain.com

# Delete a mailing list
curl \
    -X DELETE \
    --header 'X-MLMMJADMIN-API-AUTH-TOKEN: 43a89b7aa34354089e629ed9f9be0b3b' \
    http://127.0.0.1:7790/list@domain.com
```

## Manage mailing lists from command line

Script `tools/maillist_admin.py` supports basic management from command line,
pleasae run it without any argument to get detailed help information.

## Tips

mlmmj will log its operaions in 2 files under mailing list directory:

* `mlmmj.operation.log`: mlmmj logs mail sending, rejecting, subscription, etc
  in this file.
* `mlmmj-maintd.lastrun.log`: mlmmj logs maintenance related task info in this file.
