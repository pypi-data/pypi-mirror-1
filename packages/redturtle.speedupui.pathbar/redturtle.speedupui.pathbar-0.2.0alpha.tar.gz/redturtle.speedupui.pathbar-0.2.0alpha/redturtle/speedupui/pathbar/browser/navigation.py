# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFPlone import utils

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.content.browser.folderfactories import _allowedTypes

from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs as BasePhysicalNavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
from Products.CMFPlone.interfaces.constrains import IConstrainTypes

class PhysicalNavigationBreadcrumbs(BasePhysicalNavigationBreadcrumbs):
    """A complex version of basic PhysicalNavigationBreadcrumbs.
    We add here new infos to the breadcrumbs structure
    """

    def isFolderish(self, object):
        """Check if the context is a folder:
        1) has isPrincipiaFolderish attribute to True
        2) doesn't implements INonStructuralFolder
        """
        if not object.isPrincipiaFolderish:
            return False
        if hasattr(object,'__implements__') and INonStructuralFolder in object.__implements__:
            return False
        return True

    @memoize
    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        try:
            name, item_url = get_view_url(context)
        except AttributeError:
            print context
            raise

        checkPermission = getToolByName(context, 'portal_membership').checkPermission

        if container is None:
            addPerm = checkPermission(permissions.AddPortalContent, context)
            return ({'id' : context.getId(),
                     'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context),
                     'is_folderish': self.isFolderish(context),
                     'edit_perm': checkPermission(permissions.ModifyPortalContent, context),
                     'contents_perm': checkPermission(permissions.ListFolderContents, context),
                     'add_perm': addPerm,
                     #'addableTypes' : addPerm and self._itemsToAdd(context) or [],
                     'addableTypes' : addPerm and context.getAllowedTypes() or [],
                    },)

        view = getMultiAdapter((container, request), name='breadcrumbs_speedupui_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation root
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):
            addPerm = checkPermission(permissions.AddPortalContent, context)
            base += ({'id' : context.getId(),
                      'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context),
                      'is_folderish': self.isFolderish(context),
                      'edit_perm': checkPermission(permissions.ModifyPortalContent, context),
                      'contents_perm': checkPermission(permissions.ListFolderContents, context),
                      'add_perm': addPerm,
                      #'addableTypes' : addPerm and self._itemsToAdd(context) or [],
                      'addableTypes' : addPerm and context.getAllowedTypes() or [],
                     },)
        return base

