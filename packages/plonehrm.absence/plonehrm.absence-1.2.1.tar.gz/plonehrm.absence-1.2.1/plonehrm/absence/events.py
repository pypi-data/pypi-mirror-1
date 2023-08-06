from Acquisition import aq_parent

from Products.plonehrm.utils import apply_template_of_tool
from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.utils import localize

from DateTime import DateTime


def save_note(object, event):
    """ This event is fired when an absence note is created
    or updated. If a nextContactDate has been specified in the
    note, then a new item is created in the checklist.
    """
    # Only add a checklist item if we have a date or action.
    if not object.next_contact_date and not object.next_action:
        return

    # The related absence is the parent of the note.
    absence = aq_parent(object)

    # The employee is the grandfather of the note (father is absence).
    employee = aq_parent(absence)

    # We get the employee checklist.
    content_filter = {'portal_type': 'Checklist'}
    contents = list(employee.getFolderContents(contentFilter=content_filter))

    # This shall not happen as every employee has his own checklist.
    if len(contents) == 0:
        return

    checklist = contents[0].getObject()

    # Use the next action text if specified.
    # We can be sure that this is set due to the if statement at the
    # top *and* the fact that the exit form requires a nextAction if
    # the nextContactDate is entered.
    title = object.next_action

    # We create a link to add a new note in the absence.
    link_url = absence.absolute_url() + '/createObject?type_name=Note'
    link_title = _('msg_new_note_in_absence',
                   default=u'Create a new note in the related absence')
    link_title = localize(object, link_title)

    # If a next contact date is set, use it for the note.
    date = None
    if object.next_contact_date:
        # We cast python datetime to zope DateTime.
        d1 = object.next_contact_date
        date = DateTime(d1.year, d1.month, d1.day, d1.hour, d1.minute)

    # First, we check if there exists a previous item in the checklist
    # which tells to call the employee back.
    items = checklist.findItems(title, startswith = True)

    # If such an item exists, we delete it.
    for item in items:
        checklist.deleteItem(item)

    # We add the new item to the checklist.
    checklist.addItem(title,
                      date=date,
                      link_url = link_url,
                      link_title = link_title)


def apply_template(object, event):
    """After initializing an evaluation interview, set text based
    on template.
    """
    apply_template_of_tool(object, 'portal_absence')
