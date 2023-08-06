from DateTime import DateTime
from Products.Archetypes import atapi
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.file import ATFileSchema
from Products.ATContentTypes.content import schemata

from plonehrm.absence.config import PROJECTNAME
from plonehrm.absence import AbsenceMessageFactory as _

schema = atapi.Schema((
        atapi.DateTimeField(
            name='fileDate',
            required=True,
            default_method=DateTime,
            widget=atapi.CalendarWidget(
                label=_(u'label_file_date', default=u'File date'),
                show_hm = False,
                )
            ),

        ))

AbsenceFileSchema = ATFileSchema.copy() + schema

AbsenceFileSchema['title'].storage = atapi.AnnotationStorage()
AbsenceFileSchema['description'].storage = atapi.AnnotationStorage()
schemata.finalizeATCTSchema(AbsenceFileSchema)

for schema_key in AbsenceFileSchema.keys():
    if not AbsenceFileSchema[schema_key].schemata == 'default':
        AbsenceFileSchema[schema_key].widget.visible={'edit':'invisible',
                                                      'view':'invisible'}


class AbsenceFile(ATFile):

    schema = AbsenceFileSchema
    meta_type = "AbsenceFile"

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    file_date = atapi.ATDateTimeFieldProperty('fileDate')
    main_date = atapi.ATDateTimeFieldProperty('fileDate')


atapi.registerType(AbsenceFile, PROJECTNAME)
