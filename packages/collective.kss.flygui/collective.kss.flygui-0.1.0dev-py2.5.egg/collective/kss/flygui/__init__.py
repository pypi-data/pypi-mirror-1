import config
import os

import logging
LOG = logging.getLogger(config.PROJECTNAME)

if os.path.isfile(os.path.join(__path__[0], 'debug.txt')):
    class DebugFilter(logging.Filter):
        def filter(self, record):
            if record.levelno == logging.DEBUG:
                # raise level to allow going through zope logger
                record.levelno = 49
            return True
    LOG.addFilter(DebugFilter(config.PROJECTNAME))
    LOG.setLevel(logging.DEBUG)

LOG.info("Logging level set to %s",
         logging.getLevelName(LOG.getEffectiveLevel()))

from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory(config.PROJECTNAME)
