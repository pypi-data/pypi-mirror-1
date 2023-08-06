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
Access Request Objects (i.e., user(s) or group(s)).

"""


#{ Generic ARO definitions


class ARO(object):
    """
    Access Request Object.
    
    """
    
    def __init__(self, identifier, *groups):
        """
        
        :param identifier: The identifier for this ARO instance.
        
        """
        self.identifier = identifier
        self.groups = groups
    
    def get_groups(self):
        pass


# TODO: Remove this?
class CompoundARO(ARO):
    """
    Compound Access Request Object.
    
    An ARO made up of one or more AROs.
    
    """
    
    def __init__(self, *aros):
        super(CompoundARO, self).__init__(None)
        self.aros = list(aros)


#{ User AROs


class User(ARO):
    
    def __new__(cls, user_id):
        if user_id is None:
            return Anonymous.__new__()
        return AuthenticatedUser.__new__(user_id)


class AuthenticatedUser(User):
    pass


class Anonymous(User):
    def __init__(self):
        super(Anonymous, self).__init__(None)


class Anyone(User):
    def __init__(self):
        super(Anyone, self).__init__(None)


#{ Group ARO


class Group(ARO):
    pass


#}
