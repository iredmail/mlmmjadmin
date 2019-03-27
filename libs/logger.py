import logging
from logging.handlers import SysLogHandler
import settings

# Set application name.
logger = logging.getLogger('mlmmjadmin')

# Set log level.
_log_level = getattr(logging, str(settings.log_level).upper())
logger.setLevel(_log_level)

# Log format
_formatter = logging.Formatter('%(name)s %(levelname)s %(message)s')

if settings.SYSLOG_SERVER.startswith('/'):
    # Log to a local socket
    _server = settings.SYSLOG_SERVER
else:
    # Log to a network address
    _server = (settings.SYSLOG_SERVER, settings.SYSLOG_PORT)

_handler = SysLogHandler(address=_server, facility=settings.SYSLOG_FACILITY)
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
