## Script (Python) "onlinetest_process"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from DateTime import DateTime
REQUEST=context.REQUEST
answers = {}
qlist = context.getQuestionSet()
score = 0
total = 0
user = context.getUserID()
sub = context.getSubmissionRecord(user)

for question in qlist:
     answers[question.id] = REQUEST.form[question.id]
     aidx = question.getAnswer() - 1
     choices = question.getChoices()
     if choices[aidx] == answers[question.id]: score = score + 1
     total = total + 1

mark = (score * 100 // total)


context.changeSubmission(userid=user, 
                         ids=sub['questionids'],
                         started=sub['started'],
                         submitted = DateTime(),
                         mark = mark,
                         answers = answers)

return context.onlinetest_results()

