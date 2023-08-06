Description of ks.zcml.smartmenuitem:

  Author -- Anatoly Bubenkov

  Version -- $Id: README.txt 35256 2007-12-05 18:52:17Z anatoly $

  URL -- $URL: https://code.keysolutions.ru/svn/ks.zcml.smartmenuitem/trunk/src/ks/zcml/smartmenuitem/README.txt $

  Annotation:

    Product provides smartMenuItem directive, which creates menu element
    with setting root of action choosing such ways:

      - registered utility with selected interface and a name;

      - registered multi adapter with context and request to selected interface and a name;


  Realization idea:

    Directive derived from zope.app.publisher.browser.menumeta.menuItemsDirective.
    Directive uses it's own realization of menu item factory, which gets registered
    utility, or adapter as root of action.
    Parameters:

      - originUtilityInterface -- interface of registered utility;

      - originUtilityName -- name of registered utility;

      - originAdapterInterface -- interface of registered adapter;

      - originAdapterName -- name of registered adapter;

  Example of usage:

    см. ks.zcml.smartmenuitem.demo
