# -*- coding: utf-8 -*-
# $Id: interfaces.py 84149 2009-04-13 06:57:07Z glenfant $
"""Public interfaces"""

from zope.interface import Interface, Attribute
from zope.schema import Dict

class IMonkeyPatchEvent(Interface):
    """Monkey patch applied event"""

    patch_info = Dict(
        title=u"Misc information about the patch",
        description=u"""A mapping about the patch with following keys:
        * 'description': A text that describes the monkey patch
        * 'zcml_info': A text about the ZCML portion that made the patch
        * 'original': Dotted name of the original method/function.
        * 'replacement': Dotted name of the new function
        """)
