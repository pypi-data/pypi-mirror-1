from Acquisition import aq_parent

from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.utils import localize


def save_note(object, event):
    """ This event is fired when an absence note is created
    or updated. If a nextContactDate has been specified in the
    note, then a new item is created in the checklist.
    """

    # If no date for the next contact has been set, then the event
    # does not add anything in the checklist.
    if not object.next_contact_date:
        return

    # The employee is the grandfather of the note (father is absence).
    employee = aq_parent(aq_parent(object))

    # We get the employee checklist.
    content_filter = {'portal_type': 'Checklist'}
    contents = list(employee.getFolderContents(contentFilter=content_filter))

    # This shall not append as every employee has his own checklist.
    if len(contents) == 0:
        return

    checklist = contents[0].getObject()

    # We will be looking for a possibly translated string.
    title = _('msg_next_call_back_on', default=u'Call to query about absence:')
    title = localize(object, title)

    # First, we check if there exists a previous item in the checklist
    # which tells to call the employee back.
    items = checklist.findItems(title, startswith = True)

    # If such an item exists, we delete it.
    for item in items:
        checklist.deleteItem(item)

    # We add the new item to the checklist.
    toLocalizedTime = object.restrictedTraverse('@@plone').toLocalizedTime
    date = toLocalizedTime(object.next_contact_date.isoformat(),
                           long_format=True)
    checklist.addItem(title + " " + str(date))
