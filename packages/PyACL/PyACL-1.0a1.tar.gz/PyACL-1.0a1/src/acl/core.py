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
Base definitions for the Access Control Lists handling.

"""


class ACE(object):
    """
    Access Control Entry.
    
    """
    
    decisions = {
        'deny': -1,
        'allow': 1,
    }
    
    def __init__(self, aro, operation, decision, condition=None, reason=None):
        """
        
        :param aro: The ARO/subject(s) this ACE applies to.
        :param operation: The target operation on the resource in question.
        :param decision: The ACE decision (i.e., allow or deny) to be used
            when the ARO is found; see :attr:`decisions`.
        :param condition: The condition that must be met for this ACE's decision
            to be taken into account (a predicate checker or a TALES string).
        :param reason: A comment that explains the ``decision``.
        
        """
        self.aro = aro
        self.operation = operation
        self.decision = decision
        self.condition = condition
        self.reason = reason


# TODO: Turn this into a list?
# TODO: Shouldn't this be removed?
class ACL(object):
    """
    Access Control List.
    
    The collection of Access Control Entries (ACEs) assigned to a given Access
    Control Object (ACO).
    
    """
    
    # TODO: I think I should remove ``aco``
    def __init__(self, aco, aces, recursive=True):
        """
        
        :param aces: The ACEs that make up this ACL.
        
        """
        self.aces = list(aces)
        self.recursive = recursive


class AccessManager(object):
    
    def __init__(self, app_aco, acl_collection):
        self.app_aco = app_aco
        self.acl_collection = acl_collection
    
    def check_authorization(self, aco, aro, request):
        """
        Check if the ``aro`` can access ``aco`` via ``request``.
        
        """
        accepted_by_somebody = False
        
        for ace in self.acl_collection.filter_aces(aco, aro,
                                                   include_parents=True):
            # If the condition isn't met, the ACE must be ignored:
            if not ace.condition_is_met(request):
                continue
            
            # If authorization was explicitly denied, we must respect it:
            if ace.decision == ACE.decisions['deny']:
                return False
            assert ace.decision == ACE.decisions['allow']
            accepted_by_somebody = True
        
        if accepted_by_somebody:
            return True
        
        # If reached this point, we don't know what to do because no ACE
        # was found, so we have to use the fallback decision:
        return self.acl_collection.fallback_decision
