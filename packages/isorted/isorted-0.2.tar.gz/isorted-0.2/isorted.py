# coding: utf-8

# Copyright (c) 2009 Douglas Soares de Andrade <contato@douglasandrade.com>.
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

__author__ = "Douglas Soares de Andrade"
__version__ = "0.1"
__email__ = "contato@douglasandrade.com"

import locale

def isorted(items, key):
    """
    Improved sorted (Locale aware sorted)
    
    Sorts a list of dictionaries/objects by key/attribute taking locales in
    consideration.

    Example of use:
    >>> data = [{'name': u'John Doe', 'age': 20},
    ...         {'name': u'José da Silva', 'age': 25},
    ...         {'name': u'Almir Sarter', 'age': 35},
    ...         {'name': u'Solimões', 'age': 40},
    ...         {'name': u'Alírio', 'age': 10}]
    
    >>> names = isorted(data, 'name')
    >>> for item in names:
    ...     print repr(item['name'])
    u'Al\\xc3\\xadrio'
    u'Almir Sarter'
    u'John Doe'
    u'Jos\\xc3\\xa9 da Silva'
    u'Solim\\xc3\\xb5es'
    """
    
    # set the locale to be used if we have a locale set in the computer
    default_locale = locale.getdefaultlocale()
    
    if None not in default_locale:
        locale.setlocale(locale.LC_ALL, ".".join(default_locale))
    
    # Next, we sort the dictionary list, using locale-aware comparation and
    # using a lambda expression to get unicode values with a trick:
    # If the element is a dictionary it will use the dictionary get method,
    # if it is a dictionary like object (django querysets) it will use the
    # getattr builtin method to get the attribute (object.attribute).
    # IMPORTANT: It will raise an exception if the key does not exists.

    getobject = lambda x: isinstance(x,dict) and x.get(key) \
                                             or getattr(x,key)

    return sorted(items,
                  cmp=locale.strcoll,
                  key=lambda x: unicode(getobject(x)))

if __name__ == "__main__":
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
