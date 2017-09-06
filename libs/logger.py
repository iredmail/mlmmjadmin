import logging
from logging.handlers import SysLogHandler
import settings

# Set application name.
logger = logging.getLogger('mlmmj-admin')

# Set log level.
_log_level = getattr(logging, str(settings.log_level).upper())
logger.setLevel(_log_level)

# Syslog handler
if settings.SYSLOG_SERVER.startswith('/'):
    # Log to a local socket
    _handler = SysLogHandler(address=settings.SYSLOG_SERVER,
                             facility=settings.SYSLOG_FACILITY)
else:
    # Log to a network address
    _handler = SysLogHandler(address=(settings.SYSLOG_SERVER, settings.SYSLOG_PORT),
                             facility=settings.SYSLOG_FACILITY)

# Log format
_formatter = logging.Formatter('%(name)s %(levelname)s %(message)s')

_handler.setFormatter(_formatter)
logger.addHandler(_handler)
