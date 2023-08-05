"""
_syslog module (daxfi package).

This module provide utilities for logging messages.

  Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import syslog


def _sl_print(mex, prio, facil):
    """Send a message to the syslog subsystem."""
    syslog.openlog('DAXFi', syslog.LOG_PID | syslog.LOG_CONS, facil)
    syslog.syslog(prio, str(mex))
    syslog.closelog()

def sl_print_info(mex):
    """Send an informational message to the log."""
    _sl_print(mex, syslog.LOG_INFO, syslog.LOG_DAEMON)

def sl_print_warning(mex):
    """Send a warning message to the log."""
    _sl_print(mex, syslog.LOG_WARNING, syslog.LOG_DAEMON)

def sl_print_error(mex):
    """Send an error message to the log."""
    _sl_print(mex, syslog.LOG_ERR, syslog.LOG_DAEMON)


