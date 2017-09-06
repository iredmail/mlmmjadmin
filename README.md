# Mlmmj Admin

## Summary

This program runs as as WSGI server, offers:

* [Work In Progress] RESTful API interface for managing mlmmj mailing list accounts
* [Not started] web interface to allow moderators and end users to manage
  their own subscriptions.

## Requirements

* A working mail server with a working mlmmj instance.
    * For iRedMail users, please follow tutorial `docs/iredmail-integration.md`
      to integrate mlmmj.
    * Mlmmj data will be stored under `/var/spool/mlmmj`, it must be owned by
      user/group `mlmmj:mlmmj` with permission 0700.
* Python 2.6.x or 2.7.x, with extra modules:
    * web.py

## Setup mlmmj-admin

> Please follow docs under `docs/` directory to integrate mlmmj first, make
> sure it's working properly.

* Create directory used to store mlmmj-admin program:

```
mkdir -p /opt/mlmmj-admin
```

* Copy files to `/opt/mlmmj-admin`.
* Copy SysV script:

```
cd /opt/mlmmj-admin
cp rc_scripts/init.debian /etc/init.d/mlmmj-admin
chmod 0755 /etc/init.d/mlmmj-admin
systemctl enable mlmmj-admin
```

* Generate a config file by copying `settings.py.sample`:

```
cd /opt/mlmmj-admin/
cp settings.py.sample settings.py
chmod 0400 settings.py
```

* Run shell command below to generate a random string, we will use it as auth
  token which will be used by client:

```
$ echo $RANDOM | md5
43a89b7aa34354089e629ed9f9be0b3b
```

Add a new api auth token in config file `settings.py`, parameter
`api_auth_tokens`. For example:

```
auth_tokens = ['43a89b7aa34354089e629ed9f9be0b3b']
```

You can add as many token as you want.

* Choose a proper mailing list backend and add required parameters.

    * If you set `backend` to `bk_none` in config file, no addition
      config required. Other backend may requires additional parameters.
    * Backend `bk_iredmail_sql` requires few parameters to connect to
      `vmail` database on iRedMail server, please open file
      `backends/bk_iredmail_sql.py` to find the required parameters in
      the comment lines.

* After you have everything set in config file, it's ok to start `mlmmj-admin`
  service:

```
service mlmmj-admin restart
```

* TODO Log file
* TODO rsyslog config file

## Interactive with curl

```
# Create a new mailing list: list01@domain.com with preferences:
#   - name: The name of this mailing list
#   - subonlypost: only people who are subscribed to the list are allowed to post to it
curl \
    -X POST \
    --header 'X-Mlmmj-API-Token: xxxxxxxx' \
    -d "name=TestMailingList&subonlypost=yes"
    http://127.0.0.1:7779/list01@domain.com

# Delete a mailing list
curl \
    -X DELETE \
    --header 'X-Mlmmj-API-Token: xxxxxxxx' \
    http://127.0.0.1:7779/list01@domain.com

# Update a mailing list
curl \
    --header 'X-Mlmmj-API-Token: xxxxxxxx' \
    -d "closedlist=yes&closedlistsub=yes"
    http://127.0.0.1:7779/list01@domain.com
```
