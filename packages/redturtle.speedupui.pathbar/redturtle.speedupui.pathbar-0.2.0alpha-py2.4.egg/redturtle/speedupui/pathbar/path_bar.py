# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import PathBarViewlet as BasePathBarViewlet

class PathBarViewlet(BasePathBarViewlet):
    """A complex version of the Plone Pathbar viewlet, with additional features"""

    index = ViewPageTemplateFile('path_bar.pt')

    def update(self):
        ViewletBase.update(self)
        self.navigation_root_url = self.portal_state.navigation_root_url()
        self.is_rtl = self.portal_state.is_rtl()
        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_speedupui_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()

    def isAnon(self):
        """Test if the current user is Anonymous"""
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.isAnonymousUser()

    @property
    @memoize
    def portal(self):
        """Return portal object"""
        context = self.context
        return getToolByName(context, 'portal_url').getPortalObject()        

    def checkPermissionOnPortalObject(self, permission):
        """Check the given permission on Plone portal"""
        context = self.context
        mtool = getToolByName(context, 'portal_membership')
        return mtool.checkPermission(permission, self.portal)

    @property
    @memoize
    def addableTypes(self):
        """Get the addable types in the portal root"""
        return self.portal.getAllowedTypes() or []
