# Integrate Mlmmj mailing list manager in iRedMail

[TOC]

## TODO: LDAP backends

## SQL backends

Add required SQL tables in database `vmail`. Check file `SQL/*` in mlmmj-admin
package.

## Create required systeme account

```
useradd -U -m -d /var/spool/mlmmj mlmmj
chown -R mlmmj:mlmmj /var/spool/mlmmj
chmod -R 0700 /var/spool/mlmmj
```

* `-U`: create a group with the same name as the user.
* `-m`: create HOME directory.
* `-d /var/spool/mlmmj`: Specify HOME directory to `/var/spool/mlmmj`.

## Postfix integration

* `/etc/postfix/main.cf`:

```
mlmmj_destination_recipient_limit = 1

virtual_alias_maps =
    proxy:mysql:/etc/postfix/mysql/virtual_alias_maps.cf
    proxy:mysql:/etc/postfix/mysql/mlmmj.cf                 # <- Add this line
    ...

transport_maps =
    proxy:mysql:/etc/postfix/mysql/transport_maps_user.cf
    proxy:mysql:/etc/postfix/mysql/transport_maps_mlmmj.cf  # <- Add this line
    ...
```

* `/etc/postfix/mysql/mlmmj.cf`:

```
user        = vmail
password    = qsescZvV03f6YUtTMN2bQTejmjatzz
hosts       = 127.0.0.1
port        = 3306
dbname      = vmail
query       = SELECT maillists.address FROM maillists,domain WHERE maillists.address='%s' AND maillists.active=1 AND maillists.domain = domain.domain AND domain.active=1
```

* `/etc/postfix/mysql/transport_maps_mlmmj.cf`:

```
user        = vmail
password    = qsescZvV03f6YUtTMN2bQTejmjatzz
hosts       = 127.0.0.1
port        = 3306
dbname      = vmail
query       = SELECT 'mlmmj:%d/%u' FROM maillists,domain WHERE maillists.address='%s' AND maillists.active=1 AND maillists.domain = domain.domain AND domain.active=1
```

* `/etc/postfix/master.cf`:

```
# ${nexthop} is '%d/%u' in transport ('mlmmj:%d/%u')
mlmmj   unix  -       n       n       -       -       pipe
    flags=ORhu user=mlmmj argv=/usr/bin/mlmmj-receive -L /var/spool/mlmmj/${nexthop}
```

## Amavisd Integration

* Add new port `10027` in parameter `$inet_socket_port`:
* Add new policy bank `MLMMJ`, and disable spam/virus/banned/bad-header checks
  (email was scanned when it was sent from sender, so no more duplicate scannings):

```
$inet_socket_port = [10024, 10026, 10027, 9998];

$interface_policy{'10027'} = 'MLMMJ';
$policy_bank{'MLMMJ'} = {
    originating => 1,  # declare that mail was submitted by our smtp client
    allow_disclaimers => 0, # mailing list should use footer text instead.
    virus_admin_maps => ["virusalert\@$mydomain"],
    spam_admin_maps  => ["virusalert\@$mydomain"],
    smtpd_discard_ehlo_keywords => ['8BITMIME'],
    terminate_dsn_on_notify_success => 0,  # don't remove NOTIFY=SUCCESS option
    enable_dkim_signing => 1,           # sign DKIm signature
    bypass_spam_checks_maps => [1],     # don't check spam
    bypass_virus_checks_maps => [1],    # don't check virus
    bypass_banned_checks_maps => [1],   # don't check banned file names and types
    bypass_header_checks_maps => [1],   # don't check bad header
};
```

## Manage mailing list

!!! warning

    [__TODO__] ALL these managements should be done by calling the mlmmj-admin
    RESTful APIs.

### Create new mailing list

Add a new mailing list in SQL db:

```
INSERT INTO maillists (address, domain) VALUES ('alist@example.com', 'example.com');
```

Create required control files used by mlmmj:

```
mlmmj-make-ml -L 'alist' -s /var/spool/mlmmj/example.com -c mlmmj:mlmmj
```

WARNING: command `mlmmj-make-ml` won't set correct file owner and permission
for `/var/spool/mlmmj/example.com` (if this is first mailing list account) and
`/var/spool/mlmmj/example.com/alist`, you need to run `chown` and `chmod`
manually.

In `/var/spool/mlmmj/example.com/alist/control/customheaders`:

```
X-Mailinglist: alist@example.com
Reply-To: alist@example.com
```

### Subscribe a member

Add email address `user@domain.com` as a mailing list member:

```
/usr/bin/mlmmj-sub -L /var/spool/mlmmj/example.com/alist/ -a user@domain.com -c -C
```

There're more options you can use, please run `man mlmmj-sub` for details.

It will write the member email address in a file with the name of the beginning
letter of the email address getting subscribed in the `<listdir>/subscribers.d/`
directory. In our case, it's `/var/spool/mlmmj/example.com/alist/subscribed.d/u`.

### Manage mailing list profiles

Almost all profiles are controlled by plain text file, please check mlmmj
official document here: <http://mlmmj.org/docs/tunables/>

## References

* iRedMail: <http://www.iredmail.org>
* Mlmmj website: <http://mlmmj.org/>
    * Tunable parameters: <http://mlmmj.org/docs/tunables/>
    * Postfix integration: <http://mlmmj.org/docs/readme-postfix/>
