# How to integrate mlmmj-admin with your own mail server

* File `libs/mlmmj.py` handles mlmmj related data on file system. Usually you
  don't need to modify this file.

* File `backends/bk_xxx.py` handles mailing list account related data on
  your SQL/LDAP/... backend, so that your MTA (e.g. Postfix) knows it's a
  mailing list account and calls `mlmmj-receive` program to deliver the email.

    Few functions are required:

    - `def is_domain_exists(domain, conn=None):`

        Used to detect whether domain of the mailing list account exists.

    - `def is_email_exists(mail, conn=None):`

        Used to detect whether given email address exists in your backend.

    - `def is_maillist_exists(mail, conn=None):`

        Used to detect whether given mailing list account (email address)
        exists in your backend.

    - `def add_maillist(mail, form, conn=None):`

        Add required SQL/LDAP/... data in your backend to create a mailing list
        account.

    - `def remove_maillist(mail, conn=None):`

        Remove related SQL/LDAP/... data in your backend to remove a mailing list
        account.
