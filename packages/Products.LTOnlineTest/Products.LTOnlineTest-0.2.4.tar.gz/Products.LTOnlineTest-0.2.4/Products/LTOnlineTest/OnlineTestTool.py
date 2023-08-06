# $Id: OnlineTestTool.py,v 1.2 2004/08/16 05:55:22 antonh Exp $
# project: LTOnlineTest
#
# description: handles test scoring, storage and standard methods
# license: GPL
# copyright: 2004
from Products.CMFCore.utils import UniqueObject 
from OFS.SimpleItem import SimpleItem 
from Globals import InitializeClass 

class OnlineTestTool (UniqueObject, SimpleItem): 
    """ OnlineTest Tool stores grades for a particular instance """ 
    id = 'onlinetest_tool' 
    meta_type= 'OnlineTest Tool' 
    #plone_tool = 1 

    def method(self, args ...): 
        """ method ... """ 
        pass

InitializeClass(OnlineTestTool) 