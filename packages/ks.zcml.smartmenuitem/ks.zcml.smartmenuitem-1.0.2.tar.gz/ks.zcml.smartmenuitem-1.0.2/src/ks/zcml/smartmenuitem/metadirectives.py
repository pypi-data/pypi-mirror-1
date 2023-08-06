### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interface of ZCML metadirective "smartmenuitem"

$Id: metadirectives.py 23904 2007-11-27 15:42:17Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23904 $"
__date__ = "$Date: 2007-11-27 17:42:17 +0200 (Tue, 27 Nov 2007) $"

from copy import copy

from zope.interface import Interface
from zope.schema import TextLine, Field
from zope.configuration.fields import GlobalInterface
from zope.app.publisher.browser.metadirectives import IMenuItemDirective
from zope.configuration.fields import Tokens, GlobalObject

class ISmartMenuItemDirective(IMenuItemDirective):

    originUtilityInterface = GlobalInterface(
        title=u"Origin Utility Interface",
        description=u"Interface of registered utility, used for origin",
        required=False
        )

    originUtilityName = TextLine(
        title=u"Origin Utility Name",
        description=u"Name of registered utility, used for origin",
        default=u'',
        required=False
        )

    originAdapterInterface = GlobalInterface(
        title=u"Origin Adapter Interface",
        description=u"Context and request will be adapted to Interface, used for origin",
        required=False
        )

    originAdapterName = TextLine(
        title=u"Origin Adapter Name",
        description=u"Context and request will be adapted to Interface, used for origin",
        default=u'',
        required=False
        )

    selectedCondition = TextLine(
        title=u"A condition for displaying the menu item selected",
        description=u"""
        The condition is given as a TALES expression. The expression
        has access to the variables:

        context -- The object the menu is being displayed for

        request -- The browser request

        nothing -- None

        The menu item will not be displayed if there is a filter and
        the filter evaluates to a false value.""",
        required=False
        )

ISmartMenuItemDirective.setTaggedValue('keyword_arguments', True)
