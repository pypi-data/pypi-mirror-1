"""
    
    Run after Generic XML setup.
    
    Add new Kupu styles - can't use kupu.xml, because it is not additive,
    but replaces all styles once.
    
    http://www.twinapex.com

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__copyright__ = "Copyright 2008 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import string
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

styles = [
    "Tab|h2|kuputab-tab-definer",
    "Tab (open by default)|h2|kuputab-tab-definer-default",    
]

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profil
    """
        
    site = context.getSite()
    
    out = StringIO()
    
    print >> out, "Installing additional Kupu styles"
    
    kupu = site.kupu_library_tool
    for s in styles:
        # plonelibrarytool.py line 823
        s = s.strip()
        if not s in kupu.paragraph_styles:
            kupu.paragraph_styles.append(s)
            print >> out, "Installed style:" + s
            
    return out.getvalue()
    
