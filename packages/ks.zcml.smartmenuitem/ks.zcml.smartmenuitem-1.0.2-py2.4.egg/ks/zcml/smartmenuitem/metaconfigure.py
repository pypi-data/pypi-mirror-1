### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ZCML smartmenuitem directive handler

$Id: metaconfigure.py 35354 2008-12-22 23:23:43Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35354 $"
__date__ = "$Date: 2008-12-23 01:23:43 +0200 (Tue, 23 Dec 2008) $"

from zope.app.publisher.browser.menumeta import menuItemsDirective, \
                                                MenuItemFactory, \
                                                BrowserMenuItem, \
                                                BrowserSubMenuItem, \
                                                _order_counter, \
                                                Engine, \
                                                adapter
from metadirectives import ISmartMenuItemDirective
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.zapi import getUtility, absoluteURL
from zope.component import ComponentLookupError, getMultiAdapter, getAdapter
import urlparse
from zope.traversing.api import joinPath
from zope.exceptions import Unauthorized
import sys

import logging

logger = logging.getLogger('ks.zcml.smartmenuitem')

class BrowserSmartMenuItemMixin(BrowserMenuItem):
    """Browser Smart Menu Item"""

    _action = u''

    originUtilityInterface = None
    originUtilityName = None
    originAdapterInterface = None
    originAdapterName = None
    selectedCondition = None

    def setAction(self, value):
        self._action = value

    def getAction(self):
        normalized_action = self._action
        if normalized_action.startswith('@@'):
            normalized_action = normalized_action[2:]
        try:
            if self.originUtilityInterface is not None:
                origin = getUtility(self.originUtilityInterface, context=self.context, name=self.originUtilityName)
            elif self.originAdapterInterface is not None:
                try:
                    origin = getMultiAdapter((self.context, self.request), interface=self.originAdapterInterface, name=self.originAdapterName)
                except ComponentLookupError:
                    origin = getAdapter(self.context, interface=self.originAdapterInterface, name=self.originAdapterName)
            else:
                return normalized_action
            if normalized_action:
                return urlparse.urljoin('/'.join([absoluteURL(origin, self.request),'fake.html']), normalized_action)
            return '/'.join([absoluteURL(origin, self.request), normalized_action])

        except ComponentLookupError:
            logger.debug("Can't get origin object", exc_info=True)
            return '#'
        return normalized_action

    action = property(getAction, setAction)

    def selected(self):
        """See zope.app.publisher.interfaces.browser.IBrowserMenuItem"""
        res = super(BrowserSmartMenuItemMixin, self).selected()
        request_url = self.request.getURL()
        normalized_action = self.action
        if self.action.startswith('@@'):
            normalized_action = self.action[2:]
        return (res or \
               request_url == normalized_action or \
               request_url.replace('@@','') == normalized_action or \
               request_url.startswith(normalized_action)) \
                and self.selectedByCondition()

    def selectedByCondition(self):
        if self.selectedCondition is not None:
            try:
                selected = self.selectedCondition(Engine.getContext(
                    context = self.context,
                    nothing = None,
                    request = self.request,
                    modules = sys.modules,
                    ))
            except Unauthorized:
                return False
            else:
                if not selected:
                    return False
        return True

class BrowserSmartMenuItem(BrowserSmartMenuItemMixin, BrowserMenuItem):
    pass

class BrowserSmartSubMenuItem(BrowserSmartMenuItemMixin, BrowserSubMenuItem):
    pass


class smartMenuItemsDirective(menuItemsDirective):
    """Register several menu items for a particular menu."""

    def menuItem(self, _context, action, title, description=u'',
                 icon=None, filter=None, permission=None, extra=None, order=0,
                 originUtilityInterface=ISmartMenuItemDirective['originUtilityInterface'].default,
                 originUtilityName=ISmartMenuItemDirective['originUtilityName'].default,
                 originAdapterInterface=ISmartMenuItemDirective['originAdapterInterface'].default,
                 originAdapterName=ISmartMenuItemDirective['originAdapterName'].default,
                 selectedCondition=ISmartMenuItemDirective['selectedCondition'].default,
                 **kwargs
                 ):

        if originUtilityInterface is not None and originAdapterInterface is not None:
            raise ValueError("Can't specify both originUtilityInterface and originAdapterInterface")

        if filter is not None:
            filter = Engine.compile(filter)

        if selectedCondition is not None:
            selectedCondition = Engine.compile(selectedCondition)

        if order == 0:
            order = _order_counter.get(self.for_, 1)
            _order_counter[self.for_] = order + 1

        factory = MenuItemFactory(
            BrowserSmartMenuItem,
            title=title, description=description, icon=icon, action=action,
            filter=filter, permission=permission, extra=extra, order=order,
            _for=self.for_,
            originUtilityInterface=originUtilityInterface,
            originUtilityName=originUtilityName,
            originAdapterInterface=originAdapterInterface,
            originAdapterName=originAdapterName,
            selectedCondition=selectedCondition,
            **kwargs
            )
        adapter(_context, (factory,), self.menuItemType,
                (self.for_, self.layer), name=title)

    def subMenuItem(self, _context, submenu, title, description=u'',
                    action=u'', icon=None, filter=None, permission=None,
                    extra=None, order=0):

        if filter is not None:
            filter = Engine.compile(filter)

        if order == 0:
            order = _order_counter.get(self.for_, 1)
            _order_counter[self.for_] = order + 1

        factory = MenuItemFactory(
            BrowserSmartSubMenuItem,
            title=title, description=description, icon=icon, action=action,
            filter=filter, permission=permission, extra=extra, order=order,
            _for=self.for_, submenuId=submenu)
        adapter(_context, (factory,), self.menuItemType,
                (self.for_, self.layer), name=title)

def smartMenuItemDirective(_context, menu, for_,
                           action, title, description=u'', icon=None, filter=None,
                           permission=None, layer=IDefaultBrowserLayer, extra=None,
                           order=0,
                           originUtilityInterface=ISmartMenuItemDirective['originUtilityInterface'].default,
                           originUtilityName=ISmartMenuItemDirective['originUtilityName'].default,
                           originAdapterInterface=ISmartMenuItemDirective['originAdapterInterface'].default,
                           originAdapterName=ISmartMenuItemDirective['originAdapterName'].default,
                           **kwargs
                           ):
    """Smart Menu Item Directive"""
    return smartMenuItemsDirective(_context, menu, for_, layer).menuItem(
        _context, action, title, description, icon, filter,
        permission, extra, order, originUtilityInterface, originUtilityName,
        originAdapterInterface, originAdapterName, **kwargs)
