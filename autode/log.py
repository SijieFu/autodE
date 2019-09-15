"""
Set up logging with the standard python logging module. Set the log level with
$AUTODE_LOG_LEVEL = {'', INFO, WARNING, DEBUG}

i.e. export AUTODE_LOG_LEVEL=DEBUG

"""
import logging
import os


def get_log_level():
    try:
        log_level_str = os.environ['AUTODE_LOG_LEVEL']
    except KeyError:
        log_level_str = ''

    if log_level_str == 'DEBUG':
        return logging.DEBUG

    if log_level_str == 'WARNING':
        return logging.WARNING

    if log_level_str == 'INFO':
        return logging.INFO

    return logging.CRITICAL


logging.basicConfig(level=get_log_level(),
                    format='%(name)-12s: %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

# Try and use colourful logs...
try:
    import coloredlogs
    coloredlogs.install(level=get_log_level(), logger=logger)
except ImportError:
    pass
