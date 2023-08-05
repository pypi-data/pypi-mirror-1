"""
_exception module (daxfi package).

This modules defines exceptions used by the daxfi package.

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


# --- Error handling

class DaxfiError(Exception):
    """Base class for DAXFi exceptions."""
    pass

class DetectFirewallError(DaxfiError):
    """Exception raised when the Firewall class isn't able to detect
    the running firewall."""
    pass


# --- Error handling for the creation of Rule objects

class CreateRulesError(DaxfiError):
    """Exception raised when a rule cannot be built for a given firewall."""
    pass

class RemoveOptionError(DaxfiError):
    """Exception raised when we have to remove an option."""
    pass

class RemoveSectionError(DaxfiError):
    """Exception raised when we have to remove a section in a rule."""
    pass

class DaxfiStopProcessing(DaxfiError):
    """Exception raised when we have to stop processing a XML string."""
    pass


