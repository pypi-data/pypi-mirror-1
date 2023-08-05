"""
$Id: _wire.py 1530 2006-08-07 10:02:02Z hazmat $
"""

try:
    from zope.component import provideAdapter
except ImportError:
    provideAdapter = None

from interfaces import ISubversionNode, ISubversionProperties
from property import SubversionProperties

if provideAdapter is not None:
    provideAdapter( provides=ISubversionProperties,
                    adapts=(ISubversionNode,),
                    factory=SubversionProperties )

