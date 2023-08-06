import logging

logger = logging.getLogger('ExternalStorage')

def log(summary='', text='', log_level=logging.DEBUG):
    """Logs a message using Zope LOG system.
    """
    logger.log(log_level, '\n'.join(filter(None, (summary, text))))
