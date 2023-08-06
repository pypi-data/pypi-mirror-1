"""Definition of the RoundAbout Map Hotspot content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *

from AccessControl import ClassSecurityInfo

from collective.roundabout import roundaboutMessageFactory as _
from collective.roundabout.interfaces import IRoundAboutMapHotspot
from collective.roundabout.interfaces import IRoundAboutTour
from collective.roundabout.config import PROJECTNAME

RoundAboutMapHotspotSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    StringField(
        name='target_map',
        widget=SelectionWidget(
            label="Target map",
            description="Target map",
            label_msgid='label_target_map',
            description_msgid='description_target_map',
            i18n_domain='collective.roundabout',
            format='select',
        ),
        vocabulary='_getMaps',
        required=True,
    ),
    IntegerField(
        name='x',
        widget=IntegerField._properties['widget'](
            label="X-coordinate",
            description="X-coordinate in pixels of the top left corner of the hotspot on the map",
            label_msgid='label_x_hotspot',
            description_msgid='description_x_hotspot',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
        required=True,
    ),
    IntegerField(
        name='y',
        widget=IntegerField._properties['widget'](
            label="Y-coordinate",
            description="Y-coordinate in pixels of the top left corner of the hotspot on the map",
            label_msgid='label_y_hotspot',
            description_msgid='description_y_hotspot',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
        required=True,
    ),
    IntegerField(
        name='width',
        widget=IntegerField._properties['widget'](
            label="Width",
            description="Width in pixels of the hotspot on the map",
            label_msgid='label_width',
            description_msgid='description_width',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
        required=True,
    ),
    IntegerField(
        name='height',
        widget=IntegerField._properties['widget'](
            label="Height",
            description="Height in pixels of the hotspot on the map",
            label_msgid='label_height',
            description_msgid='description_height',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
        required=True,
    ),
))

RoundAboutMapHotspotSchema['title'].storage = atapi.AnnotationStorage()
RoundAboutMapHotspotSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RoundAboutMapHotspotSchema, moveDiscussion=False)

class RoundAboutMapHotspot(base.ATCTContent):
    """RoundAbout Map Hotspot"""

    security = ClassSecurityInfo()

    implements(IRoundAboutMapHotspot)

    portal_type = "RoundAbout Map Hotspot"
    schema = RoundAboutMapHotspotSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declarePrivate('_getMaps')
    def _getMaps(self):
        """Gets maps"""
        dl = DisplayList()

        parent = self.aq_inner
        while not IRoundAboutTour.providedBy(parent):
            parent = parent.getParentNode();

        for x in parent.getFolderContents():
            if x.portal_type == 'RoundAbout Map':
                dl.add(x.id, x.Title)

        return dl

atapi.registerType(RoundAboutMapHotspot, PROJECTNAME)
