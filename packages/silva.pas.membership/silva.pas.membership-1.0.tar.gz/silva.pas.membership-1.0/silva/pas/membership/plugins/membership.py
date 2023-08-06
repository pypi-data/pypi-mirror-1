# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: membership.py 28228 2008-04-04 16:24:55Z sylvain $

from zope.interface import implements


from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin

from Products.Silva.interfaces import IMember

manage_addMembershipPluginForm = PageTemplateFile("../www/membershipAddForm", 
                globals(), __name__="manage_addMembershipPluginForm")

def manage_addMembershipPlugin(self, id, title='', REQUEST=None):
    """Add a membership plugin to a Pluggable Authentication Service.
    """
    p=MembershipPlugin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=Membership+plugin+added." %
                self.absolute_url())


class MembershipPlugin(BasePlugin):
    """Plugin retrieving users defined in Silva
    """
    
    meta_type = 'Silva Membership PAS Plugin'
    security = ClassSecurityInfo()

    implements(IUserEnumerationPlugin)

    def __init__(self, id, title=None):
        self._setId(id)
        self.title=title


    def enumerateUsers(self, id=None, login=None,
                       exact_match=False,
                       sort_by=None,
                       max_results=None,
                       **kw
                       ):
        users = []
        root = self.get_root()
        members = root.Members
        if login is None:
            login = id
        for obj_id, obj in members.objectItems():
            if IMember.providedBy(obj):
                if ((exact_match and obj_id == login) or
                    (not exact_match and obj_id.startswith(login))):
                    users.append({'id': obj_id,
                                  'login': obj_id,
                                  'pluginid': self.getId()})
        return tuple(users)

