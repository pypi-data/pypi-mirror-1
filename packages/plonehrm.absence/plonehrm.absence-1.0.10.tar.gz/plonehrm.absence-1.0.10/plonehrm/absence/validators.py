from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.interfaces import INote
from zope.component import adapts


class NextActionValidator(object):
    adapts(INote)

    def __init__(self, context):
        self.context = context

    def __call__(self, request):
        """If the next contact date is selected, we need the next action text.
        """
        if request.form.get('nextContactDate_year', '0000') == '0000':
            return None
        if request.form['nextAction']:
            return None
        return {'nextAction':
                _(u'When the next action date is set, the next action '
                  u'text is mandatory.')}
