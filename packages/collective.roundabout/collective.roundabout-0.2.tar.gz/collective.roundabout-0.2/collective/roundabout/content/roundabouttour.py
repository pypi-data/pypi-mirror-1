"""Definition of the RoundAbout Tour content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *

from AccessControl import ClassSecurityInfo

from collective.roundabout import roundaboutMessageFactory as _
from collective.roundabout.interfaces import IRoundAboutTour
from collective.roundabout.config import PROJECTNAME

RoundAboutTourSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    TextField(
        name='above_content',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="Above content",
            description="Text shown above the content",
            label_msgid='label_above_content',
            description_msgid='description_above_content',
            i18n_domain='collective.roundabout',
        ),
        default_output_type='text/html',
        searchable=True,
    ),
    IntegerField(
        name='viewer_width',
        widget=IntegerField._properties['widget'](
            label="Viewer width",
            description="Width in pixels of the viewer",
            label_msgid='label_viewer_width',
            description_msgid='description_viewer_width',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
        default='320',
        required=True,
    ),
    IntegerField(
        name='viewer_height',
        widget=IntegerField._properties['widget'](
            label="Viewer height",
            description="Height in pixels of the viewer",
            label_msgid='label_viewer_height',
            description_msgid='description_viewer_height',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
        default='240',
        required=True,
    ),
    TextField(
        name='below_content',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="Below content",
            description="Text shown below the content",
            label_msgid='label_below_content',
            description_msgid='description_below_content',
            i18n_domain='collective.roundabout',
        ),
        default_output_type='text/html',
        searchable=True,
    ),
))

RoundAboutTourSchema['title'].storage = atapi.AnnotationStorage()
RoundAboutTourSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RoundAboutTourSchema, folderish=True, moveDiscussion=False)

class RoundAboutTour(folder.ATFolder):
    """Container for RoundAbout images and maps."""

    security = ClassSecurityInfo()

    implements(IRoundAboutTour)

    portal_type = "RoundAbout Tour"
    schema = RoundAboutTourSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(RoundAboutTour, PROJECTNAME)
