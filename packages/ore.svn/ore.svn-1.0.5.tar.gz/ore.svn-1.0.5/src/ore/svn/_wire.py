####################################################################
# Copyright 2002-2008 Kapil Thangavelu <kapil.foss@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
####################################################################
"""
$Id: _wire.py 2205 2008-05-07 19:44:27Z hazmat $
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

