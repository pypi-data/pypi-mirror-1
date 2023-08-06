# -*- coding: utf-8 -*-
# $Id$
"""Public interfaces"""

from zope.interface import Interface


class IManagersManager(Interface):
    """What must be provided by managers manager
    """

    def listPlonePaths():
        """Must provide la list of Zope absolute paths of all Plone sites of
        this instance/cluster
        """

    def delManager(userid):
        """Removes an user from all Plone sites
        """

    def addManager(userid, password):
        """Adds a manager to all Plone sites
        """
