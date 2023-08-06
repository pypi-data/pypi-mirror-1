###############################################################################
#
# Copyright 2006 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""
$Id: __init__.py 74003 2007-04-04 15:03:08Z dobe $
"""
__docformat__ = "reStructuredText"

from zope.app.generations.generations import SchemaManager

pkg = 'lovely.tag.generations'


schemaManager = SchemaManager(
    minimum_generation=2,
    generation=2,
    package_name=pkg)
