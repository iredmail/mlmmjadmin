# Integrate Mlmmj mailing list manager in iRedMail (LDAP backends)

[TOC]

## TODO: Migrate old mailing list to mlmmj

We're going to use existing LDAP object class `mailList` for mlmmj mailing
list, so migration is required.

* Backup LDAP data
    * For OpenLDAP, please run `/var/vmail/backup/backup_openldap.sh`
    * For OpenBSD ldapd, please run `/var/vmail/backup/backup_ldapd.sh`
* Download script to migrate all existing mailing lists. The migration script
  will:
    * Move all members to `<listdir>/subscribers.d/`
    * Set correct access control ('public', 'membersonly', 'moderatorsonly', etc)
    * Remove members from LDAP objects
    * Remove all `ou=Externals,domainName=<domain>,o=domains,dc=xx,dc=xx`

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

* /etc/postfix/ldap/virtual_group_maps.cf
* /etc/postfix/ldap/virtual_group_members_maps.cf
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

    [__TODO__] ALL these managements should be done by calling the mlmmjadmin
    RESTful APIs.

### Create a new mailing list account
### Subscribe a member
### Update mailing list settings

## References

* iRedMail: <http://www.iredmail.org>
* Mlmmj website: <http://mlmmj.org/>
    * Tunable parameters: <http://mlmmj.org/docs/tunables/>
    * Postfix integration: <http://mlmmj.org/docs/readme-postfix/>
