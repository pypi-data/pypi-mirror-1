"""Definition of the Note content type
"""

from zope.interface import implements
from DateTime import DateTime

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.interfaces import INote
from plonehrm.absence.config import PROJECTNAME

schema = atapi.Schema((
    atapi.DateTimeField(
        name='noteDate',
        required=True,
        default_method=DateTime,
        widget=atapi.CalendarWidget(
            label=_(u'label_note_date', default=u'Note date'),
            show_hm = False,
        )
    ),

    atapi.DateTimeField(
        name='nextContactDate',
        widget=atapi.CalendarWidget(
            label=_(u'label_next_contact_date', default=u'Next action at'),
        )
    ),

    atapi.StringField(
        name='nextAction',
        widget=atapi.StringWidget(
            label=_(u'label_next_action', default=u'Next action'),
            description=_(u'help_next_action',
                          default=(u'Action to perform at that date. '
                                   u'Will be used in the checklist. '
                                   u'Required if the next action date is set.'),
                          ),
        )
    ),
))

NoteSchema = schemata.ATContentTypeSchema.copy() + schema

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

NoteSchema['title'].storage = atapi.AnnotationStorage()
NoteSchema['title'].widget.visible = {'view': 'visible', 'edit': 'invisible'}
NoteSchema['title'].required = False
NoteSchema['description'].storage = atapi.AnnotationStorage()
NoteSchema['description'].required = True

schemata.finalizeATCTSchema(NoteSchema, moveDiscussion=False)

for schema_key in NoteSchema.keys():
    if not NoteSchema[schema_key].schemata == 'default':
        NoteSchema[schema_key].widget.visible={'edit':'invisible',
                                               'view':'invisible'}


class Note(base.ATCTContent):
    """Notes to add to an absence"""
    implements(INote)

    meta_type = "Note"
    schema = NoteSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('description')
    next_action = atapi.ATFieldProperty('nextAction')
    note_date = atapi.ATDateTimeFieldProperty('noteDate')
    main_date = atapi.ATDateTimeFieldProperty('noteDate')
    next_contact_date = atapi.ATDateTimeFieldProperty('nextContactDate')

    def Title(self):
        """Show the title.

        If the title field has (somehow) been set directly, then show
        that.  Otherwise show the first part of the description field.
        """
        value = self.getField('title').get(self)
        if value:
            return value
        return self.description[:20]

    def validate_nextContactDate(self, value):
        """ Validates content of next contact date. This date
        must be empty or in the future.

        >>> tomorrow = DateTime() + 1
        >>> today = DateTime()
        >>> yesterday = DateTime() - 1
        >>> note = Note('mynote')
        >>> note.validate_nextContactDate(None) is None
        True
        >>> note.validate_nextContactDate(tomorrow) is None
        True
        >>> note.validate_nextContactDate(today)
        u'The next contact date has to be in the future.'
        >>> note.validate_nextContactDate(yesterday)
        u'The next contact date has to be in the future.'
        """

        if value and DateTime().earliestTime() >= \
                DateTime(value).earliestTime():
            return _(u"The next contact date has to be in the future.")
        return None


atapi.registerType(Note, PROJECTNAME)
