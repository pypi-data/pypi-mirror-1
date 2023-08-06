"""Definition of the RoundAbout Image Hotspot content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *

from AccessControl import ClassSecurityInfo

from collective.roundabout import roundaboutMessageFactory as _
from collective.roundabout.interfaces import IRoundAboutImageHotspot
from collective.roundabout.interfaces import IRoundAboutTour
from collective.roundabout.config import PROJECTNAME

RoundAboutImageHotspotSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    StringField(
        name='target_image',
        widget=SelectionWidget(
            label="Target Image",
            description="Target image when the hotspot is clicked",
            label_msgid='label_target_image',
            description_msgid='description_target_image',
            i18n_domain='collective.roundabout',
            format='select',
        ),
        vocabulary='_getTargetImages',
    ),
    FloatField(
        name='x_angle',
        widget=IntegerField._properties['widget'](
            label="X-angle",
            description="X-angle to the next image (between 0-360)",
            label_msgid='label_x_angle',
            description_msgid='description_x_angle',
            i18n_domain='collective.roundabout',
        ),
        validators=('isDecimal',),
    ),
    FloatField(
        name='y_angle',
        widget=IntegerField._properties['widget'](
            label="Y-angle",
            description="Y-angle to the next image (between 0 and 1)",
            label_msgid='label_y_angle',
            description_msgid='description_y_angle',
            i18n_domain='collective.roundabout',
        ),
        validators=('isDecimal',),
    ),
))

RoundAboutImageHotspotSchema['title'].storage = atapi.AnnotationStorage()
RoundAboutImageHotspotSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RoundAboutImageHotspotSchema, moveDiscussion=False)

class RoundAboutImageHotspot(base.ATCTContent):
    """RoundAbout Image Hotspot"""

    security = ClassSecurityInfo()

    implements(IRoundAboutImageHotspot)

    portal_type = "RoundAbout Image Hotspot"
    schema = RoundAboutImageHotspotSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declarePrivate('_getTargetImages')
    def _getTargetImages(self):
        """Gets target images"""
        dl = DisplayList()

        parent = self.aq_inner
        while not IRoundAboutTour.providedBy(parent):
            parent = parent.getParentNode();

        for x in parent.getFolderContents():
            if x.portal_type == 'RoundAbout Image':
                dl.add(x.id, x.Title)

        return dl

atapi.registerType(RoundAboutImageHotspot, PROJECTNAME)
