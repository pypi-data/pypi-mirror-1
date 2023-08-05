# Copyright (c) 2006
# Authors:
#   Godefroid Chapelle <gotcha@bubblenet.be>
#   Balazs Ree <ree@greenfinity.hu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
__all__ = ('AzaxBaseView', 'force_unicode', 'AzaxUnicodeError', 
           'KssExplicitError', 'kssaction',
           'CommandSet', 'ICommandSet',
        ) 

import mimetypes

mimetypes.types_map['.kkt'] = 'text/xml'    # BBB legacy!
mimetypes.types_map['.kukit'] = 'text/xml'

from kss.core.azaxview import KSSView, CommandSet
from kss.core.actionwrapper import KssExplicitError, kssaction 
from kss.core.unicode_quirks import force_unicode, AzaxUnicodeError
from kss.core.interfaces import ICommandSet

# BBB
from kss.core.azaxview import AzaxBaseView

try:
    import Products.Five
except ImportError:
    pass
else:
    # Allow API to build commands from restricted code
    from AccessControl import allow_module
    allow_module('kss.core.ttwapi')

