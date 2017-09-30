# Do nothing to interactive with SQL/LDAP/... backends.


def is_domain_exists(domain, *args, **kw):
    return True


def is_email_exists(mail, *args, **kw):
    return False


def is_maillist_exists(mail, *args, **kw):
    return True


def add_maillist(mail, *args, **kw):
    return (True, )


def update_maillist(mail, *args, **kw):
    return (True, )

def remove_maillist(mail, *args, **kw):
    return (True, )
