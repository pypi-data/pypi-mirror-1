##   unimr.red5.protectedVod is copyright
##   Andreas Gabriel <gabriel@hrz.uni-marburg.de>

##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2 of the License, or
##   (at your option) any later version.

##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##   GNU General Public License for more details.

##   You should have received a copy of the GNU General Public License
##   along with this program; if not, write to the Free Software
##   Foundation, Inc., 59 Temple Place, Suite 330, Boston,
##   MA 02111-1307 USA.

"""
    Run after Generic XML setup.
    
    Add new Kupu styles - can't use kupu.xml, because it is not additive,
    but replaces all styles & resource types once.
    
    Thanks to Twinapex Research <research@twinapex.com>
              http://www.twinapex.com

    cf. plone's plonelibrarytool.py
        kupu's  librarytool.py

"""
import string
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

paragraph_styles = [
    "Red5 Stream|div|red5-stream",    
]

table_classnames = []

resource_types = { 'linkable': ('Red5Stream', ),
                   }

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profil
    """
        
    site = context.getSite()
    
    out = StringIO()
    
    print >> out, "Installing additional Kupu styles"
    
    kupu = site.kupu_library_tool
    for s in paragraph_styles:
        s = s.strip()
        if not s in kupu.paragraph_styles:
            kupu.paragraph_styles.append(s)
            print >> out, "Installed style:" + s

    for s in table_classnames:
        s = s.strip()
        if not s in kupu.table_classnames:
            kupu.table_classnames.append(s)
            print >> out, "Installed table class:" + s


    resource_type = 'linkable'   
    old_types = kupu.getPortalTypesForResourceType(resource_type)
    new_types = []
    for t in resource_types[resource_type]:
        if t not in old_types:
            new_types.append(t)

    if new_types:
        kupu.addResourceType(resource_type, list(old_types) + new_types)
        print >> out, "Installed %s resource type(s) %s" % (resource_type,new_types)
    
    return out.getvalue()
    
