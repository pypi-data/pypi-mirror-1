###############################################################################
#
# Copyright 2006 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""
$Id: __init__.py 70832 2006-10-20 05:26:04Z rogerineichen $
"""
__docformat__ = "reStructuredText"

from zope.app.generations.generations import SchemaManager

pkg = 'lovely.remotetask.generations'


schemaManager = SchemaManager(
    minimum_generation=0,
    generation=0,
    package_name=pkg)
