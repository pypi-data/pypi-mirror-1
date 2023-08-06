# $Id: Install.py,v 1.5 2004/08/19 23:36:17 antonh Exp $
# project: LTOnlineTest
#
# description: installs LTOnlineTest product
# license: GPL
# copyright: 2004
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.LTOnlineTest.config import *

from StringIO import StringIO

def install(self):
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    
    # Check that the tool has not been added using its id
    #if not hasattr(self, 'onlinetest_tool'):
    #    addTool = self.manage_addProduct['LTOnlineTest'].manage_addTool
    # Add the tool by its meta_type
    #addTool('LTOnlineTest Tool')

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
