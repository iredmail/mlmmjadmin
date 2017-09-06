# Do nothing to interactive with SQL/LDAP/... backends.

def is_domain_exists(domain, conn=None):
    return True

def is_email_exists(mail, conn=None):
    return False

def is_maillist_exists(mail, conn=None):
    return False

def add_maillist(mail, conn=None):
    return (True, )

def remove_maillist(mail, conn=None):
    return (True, )
