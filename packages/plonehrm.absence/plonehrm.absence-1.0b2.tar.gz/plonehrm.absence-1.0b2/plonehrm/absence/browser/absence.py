from datetime import date
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface

from plonehrm.absence.interfaces import IAbsenceAdapter
from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.absence import AbsenceDateError

MAXITEMS = 3


class IAbsenceListViewlet(Interface):

    def get_absence_ist():
        """Return a list of (maximum is MAXITEMS) absences"""

    def show_absence_form():
        """Return true if the absence form should be shown"""

    def show_absence_list():
        """Return true if the absence list should be shown"""

    def get_current_absence():
        """"Return the current absence, if any."""


class IAddAbsenceView(Interface):
    """Marker interface to add absencelist"""


def simple_add_absence(context, text, start_date=None):
    if text is None or text =='':
        message = _(u'msg_no_input', default=u'No input provided')
    else:
        absencelist = IAbsenceAdapter(context)
        if not isinstance(text, unicode):
            text = unicode(text, getSiteEncoding(context))
        if start_date is None:
            start_date = date.today()
        try:
            absencelist.add_absence(text, start_date)
            message = None
        except AbsenceDateError, exc:
            message = exc
    return message


def simple_close_absence(context, text=u"", end_date = None):
    """ close the open absence """
    absencelist = IAbsenceAdapter(context)
    if not isinstance(text, unicode):
        text = unicode(text, getSiteEncoding(context))
    if end_date is None:
        end_date = date.today()
    try:
        absencelist.close_absence(end_date, text = text)
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
    """A viewlet for seeing and adding absencelist."""

    template = ViewPageTemplateFile('absence_viewlet.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.context = context
        self.request = request
        self.view = view
        self.form_state = False
        self.close_form_state = False
        self.error_message = None

        self.manager = manager
        membership = getToolByName(self.context, 'portal_membership')
        self.checkPermission = membership.checkPermission
        self.encoding = getSiteEncoding(context)

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
        if self.form_state or self.close_form_state:
            return False
        return True

    def allow_adding_absence(self):
        if not self.checkPermission('plonehrm: Add absence', self.context):
            return False
        if IAbsenceAdapter(self.context).is_absent():
            return False
        return True

    def show_close_absence_button(self):
        return IAbsenceAdapter(self.context).is_absent()

    def show_add_absence_button(self):
        if not self.allow_adding_absence():
            return False
        return not self.form_state

    def show_absence_form(self):
        if not self.allow_adding_absence():
            return False
        return self.form_state

    def show_absence_close_form(self):
        return self.close_form_state

    def render(self):
        val = self.template()
        #if not isinstance(val, unicode):
        #    val = unicode(val, self.encoding)
        return val


class AbsenceList(BrowserView):
    """A view for listing the complete absencelist of an employee."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_absence_list(self):
        absencelist = self.context.get('absencelist', None)
        # Create a copy and reverse that copy, instead of mistakenly
        # reversing the original.
        result = absencelist[:]
        result.reverse()
        return result


class AbsenceAddView(PloneKSSView):
    """kss view for adding a absence"""

    @kssaction
    def add_absence(self, text, start_date, start_date_year,
                    start_date_month, start_date_day):
        """Add a absence"""
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('absencelist')
        if start_date:
            year = int(start_date_year)
            month = int(start_date_month)
            day = int(start_date_day)
            start_date = date(year, month, day)
        else:
            start_date = date.today()
        message = simple_add_absence(self.context, text, start_date)
        view = self.context.restrictedTraverse('@@plonehrm.absence')
        if message:
            view.error_message = message
            view.form_state = True        
        rendered = view.render()
        core.replaceHTML(selector, rendered)


class AbsenceCloseView(PloneKSSView):
    """kss view for closing a absence"""

    @kssaction
    def close_absence(self, text, end_date, end_date_year,
                    end_date_month, end_date_day):
        """Close the open absence"""
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('absencelist')
        if end_date:
            year = int(end_date_year)
            month = int(end_date_month)
            day = int(end_date_day)
            end_date = date(year, month, day)
        else:
            end_date = date.today()
        message = simple_close_absence(self.context, text, end_date)
        view = self.context.restrictedTraverse('@@plonehrm.absence')
        if message:
            view.error_message = message
            view.close_form_state = True        
        rendered = view.render()
        core.replaceHTML(selector, rendered)


class AbsenceKssView(PloneKSSView):
    """kss view for managing the absence viewlet"""

    @kssaction
    def kss_absence_control(self, dostate):

        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('absencelist')

        view = self.context.restrictedTraverse('@@plonehrm.absence')

        if dostate == "absenceform":
            view.form_state = True
        else:
            view.form_state = False


        if dostate == "closeabsenceform":
            view.close_form_state = True
        else:
            view.close_form_state = False

        rendered = view.render()
        core.replaceHTML(selector, rendered)
        # Set the focus on the input field, which also clears the
        # previous text entered.
        if view.form_state == True:
            core.focus('#new-absence-text')
