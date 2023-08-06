##############################################################################
#
# Enfold Enterprise Deployment - Remote Deployment of Content
# Copyright (C) 2005 Enfold Systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id: __init__.py 732 2005-01-21 19:43:40Z sidnei $
"""

import os
import sys
import logging
from logging import WARNING, INFO, DEBUG

# Values defined in ZODB.loglevels.
BLATHER = 15
TRACE = 5

logging._levelNames['TRACE'] = TRACE
logging._levelNames['BLATHER'] = BLATHER

_pid = str(os.getpid())
logger = None


def _setupLogging(level=TRACE):
    global logger
    # Configure logger for entransit.
    logger = logging.getLogger('entransit')
    logger.setLevel(level)
    fmt = logging.Formatter(
        "------\n%(asctime)s %(levelname)s %(name)s %(message)s",
        "%Y-%m-%dT%H:%M:%S")
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # Now, configure logger for ZEO.zrpc
    zeolog = logging.getLogger('ZEO.zrpc')
    zeolog.setLevel(level)
    zeolog.addHandler(handler)

def setupLogging():
    """Initialize the logging module.
    """
    global logger
    import logging.config

    # Get the log.ini file from INSTANCE_HOME/etc, the current dir,
    # fallback to sys.prefix + entransit/config
    logini = (
        os.path.join(os.getenv('INSTANCE_HOME', ''), 'etc', 'log.ini'),
        os.path.abspath("log.ini"),
        os.path.join(sys.prefix, 'entransit', 'config', 'log.ini')
        )

    found = False
    for fname in logini:
        if os.path.exists(fname):
            found = True
            logging.config.fileConfig(fname)
            break

    if not found:
        logging.basicConfig()
        level = TRACE
        if os.environ.has_key("LOGGING"):
            level = int(os.environ["LOGGING"])
        _setupLogging(level)

    if os.environ.has_key("LOGGING"):
        level = int(os.environ["LOGGING"])
        logging.getLogger().setLevel(level)

    logger = logging.getLogger('entransit')

def log(msg, level=INFO, exc_info=False):
    """Internal: generic logging function.
    """
    if logger is None:
        return
    message = "(%s) %s" % (_pid, msg)
    logger.log(level, message, exc_info=exc_info)
