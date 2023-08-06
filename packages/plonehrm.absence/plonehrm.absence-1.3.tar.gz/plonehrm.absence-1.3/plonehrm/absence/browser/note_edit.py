from zope.i18n import translate
from DateTime import DateTime
from Acquisition import aq_parent
from Products.CMFPlone import PloneMessageFactory as _pl

from Products.plonehrm.browser.base_edit import BaseEditView
from Products.plonehrm import PloneHrmMessageFactory as _p

from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.content.note import Note
from plonehrm.absence.content.note import schema
from plonehrm.absence.content.note import NoteSchema

class NoteEditView(BaseEditView):
    """ Special view to edit absence notes.
    """
    def translate_field_name(self, name):
        """ Returns the label of a field.
        """
        for field in NoteSchema.fields():
            if field.getName() == name:
                if field in self.schema.fields():
                    return translate(field.widget.label,
                                     target_language=self.lang())
                else:
                    return translate(_pl('label_' + name),
                                     target_language=self.lang(),
                                     context=self.request)
                    

    def get_form_fields(self):
        """ Provides the list of fields that should be present in
        the form
        """
        fields = ['description']
        fields.extend([f.getName() for f in schema.fields()])
        return fields

    def get_required_fields(self):
        return ['description', 'noteDate']

    def get_errors_list(self):
        """ The list of potential errors to display in the form.
        """
        lang = self.lang()
        
        # The list of potentials errors for each field.
        no_description = translate(_(u'msg_error_no_desc',
                                     default=u'You must provide a description.'),
                                   target_language=lang)

        invalid = translate(_p(u'error_invalid_date'), target_language=lang)

        nextContactPast = translate(_(u"The next contact date has to be in the future."),
                                    target_language=lang)
        
        return {'description' : {'no_description': no_description},
                'noteDate' : {'invalid' : invalid},
                'nextContactDate' : {'invalid' : invalid,
                                     'past' : nextContactPast},
                }

    def validate_form(self):
        """ Validates the form submitted when updating the employee.
        """
        fields = self.get_form_fields()
        for field in fields:
            if not field in self.form:
                # Should not happen
                return

        if not self.form['description']:
            self.errors.append('description_no_description')

        try:
            date_year = int(self.form['noteDate_year'])
            date_month = int(self.form['noteDate_month'])
            date_day = int(self.form['noteDate_day'])            
            DateTime(date_year, date_month, date_day)
        except:
            self.errors.append('noteDate_invalid')

        nextcontact = None
        try:            
            nextcontact_year = int(self.form['nextContactDate_year'])
            nextcontact_month = int(self.form['nextContactDate_month'])
            nextcontact_day = int(self.form['nextContactDate_day'])
            nextcontact_hour = int(self.form['nextContactDate_hour'])
            nextcontact_min = int(self.form['nextContactDate_minute'])

            if nextcontact_year > 0:
                nextcontact = DateTime(nextcontact_year, nextcontact_month,
                                       nextcontact_day, nextcontact_hour,
                                       nextcontact_min)
        except:
            self.errors.append('nextContactDate_invalid')

        if nextcontact and DateTime().earliestTime() >= nextcontact:
            self.errors.append('nextContactDate_past')
        
            

    def next_url(self):
        """ Redirects to the absence view, not file view.
        """
        return self.absence.absolute_url()

    def __init__(self, context, request):
        success_msg = _(u'msg_note_saved',
                        default=u'The note has been saved.')

        error_msg = _(u'error_note_saved',
                        default=u'Errors were found while saving the note.')

        BaseEditView.__init__(self, context, request, schema,
                              success_msg, error_msg)

        self.absence = aq_parent(context)
