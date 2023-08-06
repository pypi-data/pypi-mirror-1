# $Id: OnlineTest.py,v 1.9 2005/02/21 23:47:57 antonh Exp $
# project: LTOnlineTest
#
# description: models standard folder
# license: GPL
# copyright: 2004

from DateTime import DateTime
from Products.Archetypes.public import OrderedBaseFolder, BaseFolder, registerType, \
                Schema, TextField, TextAreaWidget, RichWidget
from Products.Archetypes.BaseBTreeFolder import has_btree

# BBB for CMF < 2.1
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions

from Products.CMFCore.utils import getToolByName

#from Exam class
import Globals
from Globals import PersistentMapping


OnlineTestSchema = Schema((
    TextField('description',
              searchable = 1,
              default_content_type = 'text/plain',
              default_output_type = 'text/plain',
              widget = TextAreaWidget(description = "Enter a brief description of the test.",
                                      description_msgid = "help_description",
                                      label = "Description",
                                      label_msgid = "label_description",
                                      i18n_domain="plone",
                                      rows = 5)),
    ))

class OnlineTest(BaseFolder, OrderedBaseFolder):
    """A simple folderish archetype for holding an online test"""

    __implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )
    schema = BaseFolder.schema + OnlineTestSchema
    filter_content_types = 1
    allowed_content_types = ['Question']
    meta_type = "OnlineTest"
    archetype_name = "Online Test"
    content_icon = "onlinetest_icon.gif"
    
    #TODO: add onlinetest_report action and ZPT.
    actions = ({
                    'id': 'onlinetest_contents',
                    'name': 'Manage Contents',
                    'action': 'folder_contents',
                    'permissions': (CMFCorePermissions.ListFolderContents,)
                },
                {
                    'id': 'onlinetest_attempt',
                    'name': 'Attempt Test',
                    'action': 'onlinetest_attempt',
                    'permissions': (CMFCorePermissions.View,)
                },
                {
                    'id': 'onlinetest_report',
                    'name': 'Test Report',
                    'action': 'onlinetest_report',
                    'permissions': (CMFCorePermissions.ModifyPortalContent,)
                },
              )
    
    def __init__(self, id):
        self.id = id
        self._submissions=PersistentMapping()
    
    def getUserID(self):
        """ Return the userid """
        mtool = getToolByName(self, 'portal_membership')
        
        if mtool.isAnonymousUser():
            return None
        else:    
            member = mtool.getAuthenticatedMember()
            return str(member)
        
    def all_questions(self):
        """ return the list of all available questions by order of id"""
        #should perhaps use some form of superValues or something
        q=[]
        filt = dict(portal_type=self.allowed_content_types)
        for obj in self.contentValues(filter=filt):
            q.append(obj)
        q.sort(lambda a,b: cmp(a.id,b.id))
        return q
    
    def newQuestionSet(self,userid=None):
        """"Return a question set for the user"""
        q=self.all_questions()
        return q
        
    def getQuestion(self,id):
        return getattr(self,id)
    
    def getQuestionSet(self,userid=None):
        """return the preallocated array of Exam questions for given student"""
        if userid is None: userid=self.getUserID()
        return filter(
          lambda obj,ids=self._submissions[userid]['questionids']:
          obj.id in ids
          ,self.all_questions())
    
    def changeSubmission(self,userid,ids,started=None,
                            submitted=None,mark=0,answers=None,REQUEST=None):
        """ Add or change a submission ids=question ids """
        sub=PersistentMapping()
        if started is None: started=DateTime()
        sub['started']=started
        sub['questionids']=ids
        if submitted is not None:
            sub['submitted']=submitted
            sub['mark']=mark
            sub['answers']=answers

        self._submissions[userid]=sub
        #TODO: decide what to return
        #if REQUEST is not None:
        #  return self.manage_submissions(self, REQUEST)
    
    def submission_init(self, userid=None):
        """ Set up a submission record for a particular user """
        if not hasattr(self, '_submissions'):
            self._submissions=PersistentMapping()
        if userid is None: userid=self.getUserID()
        if not self._submissions.has_key(userid):
            self.changeSubmission(
                userid, map ( lambda obj: obj['id'], self.newQuestionSet(userid) ))

    def submitCheck(self, userid=None):
        """Check that the current user is allowed to submit an exam"""
        #TODO: Version 0.3 needs submission checking
        return 1
    
    def onlinetest_submit(self, REQUEST, userid=None):
        """Take a submission and update the submission record """
        if userid is None: userid=self.getUserid()
        #self.submitCheck(userid)
        self._submissions[userid]['submitted']=DateTime()
        for qid in self._submissions[userid]['questionids']:
          getattr(self, qid).changeSubmission(userid,REQUEST,1)
        
    def getSubmissionRecord(self, userid=None):
        """ Return a hash containing student's submission record """
        if userid is None: userid=self.getUserID()
        if not self._submissions.has_key(userid): 
            self.submission_init(userid)
        sub={}
        rec=self._submissions[userid]
        for key in rec.keys():
            sub[key]=rec[key]
        #sub['timetaken']=self.timetaken(userid)
        #if sub['submitted']:
        #  sub['mark']=self.mark(userid)
        #deadline=self.getSetting('deadline')
        #sub['deadline']=deadline
        #timelimit=self.getSetting('timelimit')
        #if timelimit is not None:
        #  d=sub['started']+timelimit/1440.0
        #  if deadline is None or d<deadline: 
        #    sub['deadline']=d
        #sub['status']=self.assessmentStatus(userid)
        #if sub['deadline'] is not None:
        #  sub['remaining']=(sub['deadline']-DateTime())*1440.0
        #else:
        #  sub['remaining']=None
        return sub
        
    def deleteSubmission(self):
        """ Remove submission records for a particular set of users """
        self._submissions=PersistentMapping()
        
    def accessedIds(self):
        """list of the ids of all who have accessed the Exam"""
        return self._submissions.keys() or ()
        
    def submittedIds(self):
        """list of ids of all who have submitted (completed) the Exam"""
        return filter(
          lambda u,s=self._submissions: s[u].has_key('submitted'),
            self.accessedIds())
        
    def average_mark(self,userids=None):
        """average mark for given student list, assessed students by default"""
        if userids is None: userids=self.submittedIds()
        sum=0
        user_count = len(userids) or 1
        for userid in userids:
          sub = self.getSubmissionRecord(userid)
          if sub.has_key('mark'):
              sum=sum+sub['mark']
        return sum/user_count
        
    def timetaken(self,userid=None):
        """time taken for given student in """
        if userid is None: userid=self.getUserid()
        if not self._submissions.has_key(userid): return None
        sub= self._submissions[userid]
        if sub['submitted']:
          return 1440*(sub['submitted']-sub['started'])
        else:
          return 1440*(DateTime()-sub['started'])

registerType(OnlineTest)

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('syndication','references','metadata'):
            a['visible'] = 0
        if a['id'] == 'view':
            a['action'] = 'onlinetest_view'
    return fti
