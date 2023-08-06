# $Id: Question.py,v 1.5 2005/02/21 23:48:03 antonh Exp $
# project: LTOnlineTest
#
# description: models standard folder
# license: GPL
# copyright: 2004

#from Products.Archetypes.public import BaseSchema, Schema
#from Products.Archetypes.public import TextField, LinesField, IntegerField
#from Products.Archetypes.public import LinesWidget, IntegerWidget, TextAreaWidget, RichWidget
#from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.public import *                 


QuestionSchema = Schema((
    TextField('question-text',
              searchable=True,
              required=True,
              accessor='getQuestionText',
              mutator='setQuestionText',
              default_content_type = 'text/html',
              default_output_type = 'text/html',
              allowable_content_types = ('text/structured',
                                         'text/restructured',
                                         'text/html',
                                         'text/plain',),
              widget=RichWidget(label = "Question Text",
                                description= "Enter the text of the question here",
                                rows = 5),
              ),
    LinesField('choices',
			   required=1,
			   widget=LinesWidget(description="Enter each alternative on a new line",
			                      label='Choices'),
			   ),
	IntegerField('answer',
				 required=1,
				 widget=IntegerWidget(description = "Row number of the correct answer",
				                      label='Correct Answer'),
				 ),
    TextField('explanation',
              searchable = 0,
              default_content_type = 'text/plain',
              default_output_type = 'text/plain',
              widget = TextAreaWidget(description = "Explanation of the correct answer",
                                      description_msgid = "help_explanation",
                                      label = "Explanation",
                                      label_msgid = "label_explanation",
                                      i18n_domain="plone",
                                      rows = 5)),
    ))

class Question(BaseContent):
    """A simple multiple choice question"""

    #__implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )
    schema = BaseSchema + QuestionSchema
    global_allow = 0
    meta_type = "Question"
    archetype_name = "Question"
    content_icon = "question_icon.gif"

registerType(Question)

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('syndication','references','metadata'):
            a['visible'] = 0

    # change view to assignment listing
    for a in fti['actions']:
        if a['id'] == 'view':
            a['action'] = 'question_view'
    return fti


