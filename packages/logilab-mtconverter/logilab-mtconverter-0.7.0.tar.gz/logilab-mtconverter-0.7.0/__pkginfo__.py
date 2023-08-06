"""
Copyright (c) 2006-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr

mtconverter packaging information
"""

modname = "mtconverter"
distname = "logilab-mtconverter"
subpackage_of = 'logilab'
numversion = (0, 7, 0)
version = '.'.join([str(num) for num in numversion])

license = 'GPL'
copyright = '''Copyright (c) 2006-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Sylvain Thenault"
author_email = "contact@logilab.fr"

short_desc = "a library to convert from a MIME type to another"
long_desc = """This package is originally a backport of Zope's PortalTransforms tool with
all Zope's internal removed (e.g. most of the code).
"""
web = "http://www.logilab.org/project/logilab-mtconverter"
