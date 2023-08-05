"""
$Id: __init__.py 1536 2006-08-07 21:00:35Z hazmat $
"""

from context import SubversionContext

# wire up zope3 components in code, to allow for easy usage outside of zope.
import _wire
del _wire

