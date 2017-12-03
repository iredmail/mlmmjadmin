# Run a WSGI server for mlmmj RESTful API and web interface.

import os
import sys
import pwd
import grp

import web

rootdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, rootdir)

# Directory which stores mailing list backends.
sys.path.insert(0, os.path.join(rootdir, 'backends'))

import settings
from libs import __version__
from libs.logger import logger
from controllers.urls import urls

web.config.debug = settings.DEBUG

# Make sure required directories exists.
for _dir in [settings.MLMMJ_SPOOL_DIR, settings.MLMMJ_SKEL_DIR]:
    if not os.path.exists(_dir):
        sys.exit("ERROR: directory doesn't exist: {}.".format(_dir))

os.umask(0077)

# Get uid/gid of daemon user.
uid = pwd.getpwnam(settings.run_as_user).pw_uid
gid = grp.getgrnam(settings.run_as_group).gr_gid

# Run as daemon user
os.setgid(gid)
os.setuid(uid)

app = web.application(urls, globals())

if __name__ == '__main__':
    # Starting webpy builtin http server.
    listen_address = settings.listen_address
    listen_port = int(settings.listen_port)

    logger.info('Starting mlmmj-admin, version {}, listening on {}:{}.'.format(
        __version__, listen_address, listen_port))
    web.httpserver.runsimple(app.wsgifunc(), (listen_address, listen_port))
else:
    # Run as a WSGI application
    application = app.wsgifunc()
