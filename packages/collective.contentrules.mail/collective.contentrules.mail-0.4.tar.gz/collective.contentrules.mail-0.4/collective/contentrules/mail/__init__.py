# -*- coding: utf-8 -*-
# Copyright (c) 2008 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Initialize logger
import os
import logging
from config import PROJECTNAME

LOG = logging.getLogger(PROJECTNAME)

if os.path.isfile(os.path.join(__path__[0], 'debug.txt')):
    class DebugFilter(logging.Filter):
        def filter(self, record):
            if record.levelno == logging.DEBUG:
                # raise level to allow going through zope logger
                record.levelno = 49
            return True
    LOG.addFilter(DebugFilter(PROJECTNAME))
    LOG.setLevel(logging.DEBUG)

LOG.info("Logging level set to %s",
         logging.getLevelName(LOG.getEffectiveLevel()))

from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory(PROJECTNAME)
