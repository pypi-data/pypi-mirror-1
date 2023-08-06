# -*- coding: utf-8 -*-
# $Id$
"""Managers management utilities"""

from zope.interface import implements
from zope.app.container.interfaces import IContainer
from Products.Five.browser import BrowserView
from interfaces import IManagersManager

class ManagersManager(BrowserView):

    implements(IManagersManager)

    def listPlonePaths(self):
        """see IManagersManager
        """
        out = self._listPlonePaths()
        return out, True, ''

    def _listPlonePaths(self):
        out = []
        plone_mt = 'Plone Site'
        for obj in getPloneSites(self.context):
            path = '/'.join(obj.getPhysicalPath())
            out.append(path)
        return out

    def delManager(self, userid):
        """see IManagersManager
        """
        success = True
        paths = self._listPlonePaths()
        for path in paths:
            plone = self.context.restrictedTraverse(path)
            plone_pas = plone.acl_users
            # Note that PlonePAS does silently nothing if the user doesn't exist
            plone_pas.userFolderDelUsers([userid])
        return success, ""

    def addManager(self, userid, password):
        """see IManagersManager
        """
        success = True
        paths = self._listPlonePaths()
        for path in paths:
            plone = self.context.restrictedTraverse(path)
            plone_pas = plone.acl_users
            # Note that PlonePAS does silently nothing if the user doesn't exist
            plone_pas.userFolderAddUser(userid, password, ['Manager'], [])
        return success, ""



def getPloneSites(folderish):
    """Plone sites that are in that folderish
    """
    sites = []
    for item in folderish.objectValues():
        if item.meta_type == 'Plone Site':
            sites.append(item)
        elif IContainer.providedBy(item):
            sites.extend(getPloneSites(item))
    return sites
