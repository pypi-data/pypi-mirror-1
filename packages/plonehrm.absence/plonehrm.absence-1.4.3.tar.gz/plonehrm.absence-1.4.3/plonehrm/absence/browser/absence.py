from DateTime import DateTime
from datetime import date
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.i18n import translate

from plonehrm.absence.interfaces import IAbsenceAdapter
from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.absence import AbsenceDateError

MAXITEMS = 3


class IAbsenceListViewlet(Interface):

    def get_absence_ist():
        """Return a list of (maximum is MAXITEMS) absences
        """

    def show_absence_form():
        """Return true if the absence form should be shown
        """

    def show_absence_list():
        """Return true if the absence list should be shown
        """

    def get_current_absence():
        """Return the current absence, if any.
        """


class IAddAbsenceView(Interface):
    """Marker interface to add absencelist
    """


def simple_add_absence(context, text, start_date=None, is_accident=False,
                       first_day_percentage=1,
                       percentage_absence=100, percentage_productivity=0):
    if text is None or text =='':
        message = _(u'msg_no_input', default=u'No input provided')
    else:
        absencelist = IAbsenceAdapter(context)
        if not isinstance(text, unicode):
            text = unicode(text, getSiteEncoding(context))
        if start_date is None:
            start_date = date.today()
        try:
            absencelist.add_absence(text, start_date, is_accident,
                                    first_day_percentage,
                                    percentage_absence, percentage_productivity)
            message = None
        except AbsenceDateError, exc:
            message = exc
    return message


def simple_close_absence(context, length=None, end_date = None):
    """ close the open absence
    """
    absencelist = IAbsenceAdapter(context)
    if end_date is None:
        end_date = date.today()
    try:
        absencelist.close_absence(end_date, length)
        message = None
    except AbsenceDateError, exc:
        message = exc
    return message


class AddAbsence(BrowserView):
    """Add an Absence.

    Note that this is the non-kss version.  We may want to concentrate
    on the kss version instead (see below).
    """

    def __call__(self):
        """Create a new Absence if the inline form is used.

        Only react if the form was submitted
        Only react if someone filled in text for the Absence
        Make a new Absence with the correct text and date.
        When not set, the date will be set to today.
        """
        text = self.request.get('text', None)
        start_date = self.request.get('new_absence_date', None)
        if start_date:
            year = int(self.request.get('new_absence_date_year'))
            month = int(self.request.get('new_absence_date_month'))
            day = int(self.request.get('new_absence_date_day'))
            start_date = date(year, month, day)
        else:
            start_date = date.today()
        message = simple_add_absence(self.context, text, start_date)
        self.context.plone_utils.addPortalMessage(message)
        response = self.request.response
        here_url = self.context.absolute_url()
        response.redirect(here_url)


class AbsenceViewlet(Explicit):
    """A viewlet for seeing and adding absencelist.
    """

    template = ViewPageTemplateFile('absence_viewlet.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.context = context
        self.request = request
        self.view = view
        self.form_state = False
        self.close_form_state = False
        self.edit_form_state = False
        self.error_message = None

        # List of possible status, each one defines how the viewlet
        # is rendered.
        self.status_list = ['list',
                            'add_form',
                            'edit_form',
                            'close_form',
                            'percentage_form']
        self.status = 'list'

        self.manager = manager
        membership = getToolByName(self.context, 'portal_membership')
        self.checkPermission = membership.checkPermission
        self.encoding = getSiteEncoding(context)

    def set_status(self, status):
        """ Changes the way the viewlet is rendered.
        """
        if status == 'add_form' and not self.can_add_absences():
            status = 'list'
        elif status in ['edit_form', 'percentage_form'] and \
                 not self.can_edit_absences():
            status = 'list'
        elif status == 'close_form' and not self.can_close_absences():
            status = 'list'
        elif status in self.status_list:
            self.status = status

    def get_absence_list(self):
        absences = IAbsenceAdapter(self.context)
        absencelist = absences.absencelist
        result = absencelist[-MAXITEMS:]
        result.reverse()
        return result

    def get_current_absence(self):
        absences = IAbsenceAdapter(self.context)
        return absences.current_absence()

    def show_absence_list(self):
        return self.status == 'list'

    def can_add_absences(self):
        return self.checkPermission('plonehrm: Add absence', self.context)

    def can_edit_absences(self):
        return self.checkPermission('plonehrm: Modify absence', self.context)

    def can_close_absences(self):
        return self.checkPermission('plonehrm: close absence', self.context)


    def allow_adding_absence(self):
        if not self.can_add_absences():
            return False
        if IAbsenceAdapter(self.context).is_absent():
            return False
        return True

    def show_percentage_button(self):
        return IAbsenceAdapter(self.context).is_absent() and \
               self.can_edit_absences()

    def show_close_absence_button(self):
        return IAbsenceAdapter(self.context).is_absent() and \
               self.can_close_absences()

    def show_add_absence_button(self):
        if not self.allow_adding_absence():
            return False
        return self.status == 'list'

    def show_absence_form(self):
        if not self.allow_adding_absence():
            return False
        return self.status == 'add_form'

    def show_absence_close_form(self):
        if not self.can_close_absences():
            return False
        return self.status == 'close_form'

    def show_absence_edit_form(self):
        if not self.can_edit_absences():
            return False       
        return self.status == 'edit_form'

    def show_absence_percentage_form(self):
        if not self.can_edit_absences():
            return False       
        return self.status == 'percentage_form'

    def is_arbo(self):
        """ Checks if the user has Arbo manager rights.
        """
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission('plonehrm: manage Arbo content',
                                          self.context)

    def render(self):
        val = self.template()
        #if not isinstance(val, unicode):
        #    val = unicode(val, self.encoding)
        return val


class AbsenceList(BrowserView):
    """ A view for listing the complete absencelist of an employee."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_absence_list(self):
        absences = IAbsenceAdapter(self.context)
        absencelist = absences.absencelist
        # Create a copy and reverse that copy, instead of mistakenly
        # reversing the original.
        result = absencelist[:]
        result.reverse()
        return result


class AbsenceKss(PloneKSSView):
    """ This class contains every KSS views used in the absence
    viewlet.
    """

    @property
    def lang(self):
        props = getToolByName(self.context, 'portal_properties')
        return props.site_properties.getProperty('default_language')

    def refresh_viewlet(self, status = 'list'):
        """ Sets the view to the asked status and refreshes it.
        """
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('absencelist')

        # Get and configure the view.
        view = self.context.restrictedTraverse('@@plonehrm.absence')
        view.set_status(status)

        # Display it.
        rendered = view.render()
        core.replaceHTML(selector, rendered)

    @kssaction
    def show_list(self):
        """ Shows the list of absences.
        """
        self.refresh_viewlet('list')

    @kssaction
    def show_add_form(self):
        """ Shows the form to add an absence.
        """
        self.refresh_viewlet('add_form')

    @kssaction
    def show_edit_form(self):
        """ Shows the form to edit an absence.
        """
        self.refresh_viewlet('edit_form')

    @kssaction
    def show_close_form(self):
        """ Shows the form to close an absence.
        """
        self.refresh_viewlet('close_form')

    @kssaction
    def show_percentage_form(self):
        """ Shows the form to update percentages of absence/productivity.
        """
        self.refresh_viewlet('percentage_form')

    @kssaction
    def cancel(self):
        """ Hides the existing status message and refreshes
        the viewlet.
        """
        self.getCommandSet('plone').issuePortalMessage('')
        self.show_list()


    def validate_add_or_edit_form(self, form, add=False):
        """ Checks that the form submitted when adding
        or editing an absence is correct.
        """

        # Checks that every field has been submitted.
        fields = ['text',
                  'new_absence_date',
                  'new_absence_date_year',
                  'new_absence_date_month',
                  'new_absence_date_day']

        if add:
            fields.extend(['first_day_percentage',
                           'percentage_absence',
                           'percentage_productivity'])
            
        for field in fields:
            if not field in form:
                # Should not happen.
                return
            
        errors = []
        # Check that a title has been provided.
        if not form['text']:
            errors.append('absence_viewlet_error_no_description')

        # Check that the date is valid.
        if form['new_absence_date']:
            year = int(form['new_absence_date_year'])
            month = int(form['new_absence_date_month'])
            day = int(form['new_absence_date_day'])

            try:
                start_date = date(year, month, day)
            except:
                errors.append('absence_viewlet_error_invalid_date')
                start_date = date.today()
        else:
            start_date = date.today()

        # Check that the start date is tomorrow or earlier.
        if start_date.toordinal() > date.today().toordinal() + 1:
            errors.append('absence_viewlet_error_date_future')

        if add:
            # Check that the percentage of unworked time for first day
            # in correct.
            try:
                first_day_percentage = float(form['first_day_percentage'])
            except ValueError:
                first_day_percentage = 0

            if not first_day_percentage in [x/4.0 for x in range(1, 5)]:
                errors.append(
                    'absence_viewlet_error_invalid_first_day_percentage')
            
            # Checks that percentages are correct.
            percentage_absence = 0
            percentage_productivity = 0
            
            try:
                percentage_absence = int(form['percentage_absence'])
            except:
                errors.append(
                    'absence_viewlet_error_invalid_absence_percentage')
                
            try:
                percentage_productivity = int(form['percentage_productivity'])
            except:
                errors.append(
                    'absence_viewlet_error_invalid_productivity_percentage')

            if percentage_absence < 0 or \
               percentage_absence > 100:
                errors.append(
                    'absence_viewlet_error_invalid_absence_percentage')

            if percentage_productivity < 0 or \
               percentage_productivity > 100:
                errors.append(
                    'absence_viewlet_error_invalid_productivity_percentage')
                
        return (start_date, errors)

    def clear_errors(self):
        """ Hides every errors displayed in the form.
        """
        errors = ['absence_viewlet_error_no_description',
                  'absence_viewlet_error_invalid_date',
                  'absence_viewlet_error_conflict_date',
                  'absence_viewlet_error_date_future',
                  'absence_viewlet_error_length_null',
                  'absence_viewlet_error_length_no_integer',
                  'absence_viewlet_error_end_date_before_start_date',
                  'absence_viewlet_error_invalid_absence_percentage',
                  'absence_viewlet_error_invalid_productivity_percentage',
                  'absence_viewlet_error_date_before_previous_percentage',
                  'absence_viewlet_error_invalid_first_day_percentage']

        core = self.getCommandSet('core')
        for error in errors:
            selector = core.getHtmlIdSelector(error)
            core.setAttribute(selector, 'class', 'dont-show')

        selector = core.getHtmlIdSelector('absence_viewlet_global_error')
        core.setAttribute(selector, 'class', 'dont-show')
        core.replaceInnerHTML(selector, '')
        

    def show_errors(self, errors = [], global_error = ''):
        """ Show errors found while validating the form.
        """
        # Clears the previous errors.
        self.clear_errors()
        
        core = self.getCommandSet('core')
        for error in errors:
            selector = core.getHtmlIdSelector(error)
            core.setAttribute(selector, 'class', 'errormessage')

        if global_error:
            selector = core.getHtmlIdSelector('absence_viewlet_global_error')
            core.setAttribute(selector, 'class', 'errormessage')
            core.replaceInnerHTML(selector, global_error)

        status = translate(_(u'msg_absence_error',
                             u'Error have been found while saving the absence'),
                           target_language = self.lang)
        
        self.getCommandSet('plone').issuePortalMessage(status,
                                                       msgtype='Error')

    @kssaction
    def add_absence(self):
        """ Creates the new absence and displays the list again.
        """
        form = self.request.form

        try:
            start_date, errors = self.validate_add_or_edit_form(form, add=True)
        except TypeError:
            # Happens when validate_form returned None, meaning
            # that the form has not been correctly submitted.
            # This should not happen.
            return

        # Checks that the date does not conflict with the previous
        # absence.
        absence_list_view = self.context.restrictedTraverse('@@absencelist')
        absence_list = absence_list_view.get_absence_list()

        if (absence_list and
            start_date.toordinal() <= \
            absence_list[0].end_date.toordinal()):
            errors.append("absence_viewlet_error_conflict_date")

        if errors:
            self.show_errors(errors = errors)
            return

        is_accident = 'is_accident' in form
        first_day_percentage = form['first_day_percentage']
        percentage_absence = form['percentage_absence']
        percentage_productivity = form['percentage_productivity']

        # Now we can add the absence.
        message = simple_add_absence(self.context, form['text'],
                                     start_date, is_accident,
                                     first_day_percentage,
                                     percentage_absence,
                                     percentage_productivity)

        if message:
            # Should not happen.
            self.show_errors(global_error = message)
            return

        # Display the status success message.
        status = translate(_(u'msg_absence_added',
                             u'Absence added'),
                           target_language = self.lang)
        self.getCommandSet('plone').issuePortalMessage(status)

        # Shows the list again.
        self.show_list()

    @kssaction
    def edit_absence(self):
        """ Updates the current absence text and start date.
        """
        form = self.request.form
        try:
            start_date, errors = self.validate_add_or_edit_form(form)
        except TypeError:
            # Happens when validate_form returned None, meaning
            # that the form has not been correctly submitted.
            # This should not happen.
            return

        # Get the absence list.
        absence_list_view = self.context.restrictedTraverse('@@absencelist')
        absence_list = absence_list_view.get_absence_list()
        if not absence_list:
            # Should not happen.
            return
        
        # Checks that the date does not conflict with the previous
        # absence. As we edit the current absence (which is the last one),
        # the previous absence is absencelist[1].
        if (len(absence_list) > 1 and
            start_date.toordinal() <= \
            absence_list[1].end_date.toordinal()):
            errors.append("absence_viewlet_error_conflict_date")

        if errors:
            self.show_errors(errors = errors)
            return

        current_absence = absence_list[0]
        current_absence.title = form['text']
        current_absence.start_date = start_date

        # Display the status success message.
        status = translate(_(u'msg_absence_edited',
                             u'Absence edited'),
                           target_language = self.lang)
        self.getCommandSet('plone').issuePortalMessage(status)

        # Shows the list again.
        self.show_list()

    @kssaction
    def close_absence(self):
        """ Closes the current absence.
        """
        def quarter_round(f):
            """ Takes a float and returns it rounded to the quarter
                x.0, x.25, x.50, x.75.
                Note: it is rounded to the lowest quarter, so 0.89 will
                be rouned as 0.75, not 1.
            """
            int_part = int(f)
            float_part = f - int_part
            
            for i in range(0, 5):
                if float_part > (0.25 * (i - 1)) and float_part < (0.25 * i):
                    float_part = i and 0.25 * (i - 1) or 0.0
                    break

            return int_part + float_part

        
        form = self.request.form

        absence_list_view = self.context.restrictedTraverse('@@absencelist')
        absence_list = absence_list_view.get_absence_list()

        if not absence_list:
            # Should not happen.
            return
        current_absence = absence_list[0]

        # Checks that every fields 
        fields = ['absence_length',
                  'close_absence_date',
                  'close_absence_date_year',
                  'close_absence_date_month',
                  'close_absence_date_day']

        for field in fields:
            if not field in form:
                # Should not happen.
                return

        errors = []

        # Check that the length is valid.
        try:
            length = '.'.join(form['absence_length'].split(','))
            absence_length = float(length)
        except:
            errors.append('absence_viewlet_error_length_no_integer')
            absence_length = 1

        absence_length = quarter_round(absence_length)

        if not absence_length > 0:
            errors.append('absence_viewlet_error_length_null')

        # Check that the date is valid and correct.
        if form['close_absence_date']:
            year = int(form['close_absence_date_year'])
            month = int(form['close_absence_date_month'])
            day = int(form['close_absence_date_day'])

            try:
                end_date = date(year, month, day)
            except:
                errors.append('absence_viewlet_error_invalid_date')
                end_date = date.today()
        else:
            end_date = date.today()
        
        # Check that the end date is after the start date.
        if end_date.toordinal() < current_absence.start_date.toordinal():
            errors.append('absence_viewlet_error_end_date_before_start_date')
            
        if errors:
            self.show_errors(errors=errors)
            return

        # Close the absence.
        message = simple_close_absence(self.context, absence_length,
                                       end_date)

        if message:
            # Should not happen.
            self.show_errors(global_error = message)
            return

        # Display the status success message.
        status = translate(_(u'msg_absence_closed',
                             u'Absence closed'),
                           target_language = self.lang)
        self.getCommandSet('plone').issuePortalMessage(status)

        # Shows the list again.
        self.show_list()

    @kssaction
    def add_percentage(self):
        form = self.request.form

        absence_list_view = self.context.restrictedTraverse('@@absencelist')
        absence_list = absence_list_view.get_absence_list()

        if not absence_list:
            # Should not happen.
            return
        current_absence = absence_list[0]
        current_absence_percentage = current_absence.percentage_list

        # Check that all fields have been submitted.
        fields = ['percentage_absence',
                  'percentage_productivity',
                  'absence_percentage_date_year',
                  'absence_percentage_date_month',
                  'absence_percentage_date_day']

        for field in fields:
            if not field in form:
                #Should not happen.
                return

        
        # We clear the previous errors.
        self.clear_errors()

        # We validate the form.
        errors = []
        percentage_absence = 0
        percentage_productivity = 0
        
        try:
            percentage_absence = int(form['percentage_absence'])
        except:
            errors.append('absence_viewlet_error_invalid_absence_percentage')

        try:
            percentage_productivity = int(form['percentage_productivity'])
        except:
            errors.append(
                'absence_viewlet_error_invalid_productivity_percentage')

        if percentage_absence < 0 or \
               percentage_absence > 100:
            errors.append(
                'absence_viewlet_error_invalid_absence_percentage')

        if percentage_productivity < 0 or \
               percentage_productivity > 100:
            errors.append(
                    'absence_viewlet_error_invalid_productivity_percentage')


        percentage_date = None
        try:
            year = int(form['absence_percentage_date_year'])
            month = int(form['absence_percentage_date_month'])
            day = int(form['absence_percentage_date_day'])
            percentage_date = date(year, month, day)
        except:
            errors.append('absence_viewlet_error_invalid_date')

        # Check that the date does not conflict.
        if percentage_date and \
               percentage_date.toordinal() < \
               current_absence.current_percentage().date.toordinal():
            errors.append(
                'absence_viewlet_error_date_before_previous_percentage')

        if errors:
            self.show_errors(errors=errors)
            return

        current_absence.add_percentage(percentage_date, percentage_absence,
                                       percentage_productivity)

        # Display the status success message.
        status = translate(_(u'msg_absence_percentage_added',
                             u'Percentages of absence and productivity ' + \
                             'have been updated'),
                           target_language = self.lang)
        self.getCommandSet('plone').issuePortalMessage(status)

        # Shows the list again.
        self.show_list()
        
    @kssaction
    def delete_percentage(self, id):
        try:
            percentage_id = int(id.split('_')[-1])
        except:
            # Should not happen.
            return

        absence_list_view = self.context.restrictedTraverse('@@absencelist')
        absence_list = absence_list_view.get_absence_list()

        if not absence_list:
            # Should not happen.
            return
        current_absence = absence_list[0]
        percentage_list = current_absence.percentage_list

        i = 0
        for percentage in percentage_list:
            if percentage.id == percentage_id:
                break
            i += 1
            
        if i == len(percentage_list):
            # Should not happen.
            return

        percentage_list.pop(i)
        
        # Display the status success message.
        status = translate(_(u'msg_absence_percentage_removed',
                             u'Percentages of absence and productivity ' + \
                             'have been removed'),
                           target_language = self.lang)
        self.getCommandSet('plone').issuePortalMessage(status)
        
        self.show_percentage_form()
        
