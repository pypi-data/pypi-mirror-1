# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of PyACL <http://code.gustavonarea.net/pyacl/>
#
# PyACL is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.
#
# PyACL is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyACL. If not, see <http://www.gnu.org/licenses/>.

"""
PyACL exceptions.

"""


class PyACLException(Exception):
    """Base class for the exceptions raised by PyACL and its plugins."""
    pass


#{ ACL-specific exceptions


class ExistingACOError(PyACLException):
    """
    Exception raised when trying to add an existing subresource or operation
    in a resource.
    
    """
    pass


class NoACOMatchError(PyACLException):
    """
    Exception raised when a non-existing subresource or operation is requested
    to a resource.
    
    """
    pass


#{ Source adapters-related exceptions


class AdapterError(PyACLException):
    """Base exception for problems the source adapters."""
    pass


class SourceError(AdapterError):
    """
    Exception for problems with the source itself.
    
    .. attention::
        If you are creating a :term:`source adapter`, this is the only
        exception you should raise.
    
    """
    pass


class ExistingGroupError(AdapterError):
    """Exception raised when trying to add an existing group."""
    pass


class NonExistingGroupError(AdapterError):
    """Exception raised when trying to use a non-existing group."""
    pass


class UserPresentError(AdapterError):
    """
    Exception raised when trying to add a user to a group that already
    contains it.
    
    """
    pass


class UserNotPresentError(AdapterError):
    """
    Exception raised when trying to remove a user from a group that 
    doesn't contain it.
    
    """
    pass


#}
