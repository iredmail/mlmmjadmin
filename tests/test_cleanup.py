import os
from .utils import remove_ml
from . import data


def test_cleanup():
    remove_ml()

    domain_dir = '/var/vmail/mlmmj/' + data.domain
    try:
        os.rmdir(domain_dir)
    except Exception as e:
        print("Failed to remove testing data for domain {}: {}".format(data.domain, repr(e)))
