"""Definition of the RoundAbout Image content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import DisplayList
from Products.Archetypes.atapi import *

from Products.CMFPlone.utils import log

from AccessControl import ClassSecurityInfo

from collective.roundabout import roundaboutMessageFactory as _
from collective.roundabout.interfaces import IRoundAboutImage
from collective.roundabout.interfaces import IRoundAboutTour
from collective.roundabout.config import PROJECTNAME

RoundAboutImageSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    ImageField(
        name='image',
        widget=PhotoField._properties['widget'](
            label="Image",
            description="360 degree image",
            label_msgid='label_image',
            description_msgid='description_image',
            i18n_domain='collective.roundabout',
        ),
        storage=AttributeStorage(),
        max_size=(10000,10000),
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        required=True,
    ),
    StringField(
        name='map',
        widget=SelectionWidget(
            label="Map",
            description="Map on which the image is located",
            label_msgid='label_map',
            description_msgid='description_map',
            i18n_domain='collective.roundabout',
            format='select',
        ),
        vocabulary='_getMaps',
    ),
    IntegerField(
        name='mapx',
        widget=IntegerField._properties['widget'](
            label="X-coordinate on the map",
            description="X-coordinate in pixels on the map",
            label_msgid='label_mapx',
            description_msgid='description_mapx',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
    ),
    IntegerField(
        name='mapy',
        widget=IntegerField._properties['widget'](
            label="Y-coordinate on the map",
            description="Y-coordinate in pixels on the map",
            label_msgid='label_mapy',
            description_msgid='description_mapy',
            i18n_domain='collective.roundabout',
        ),
        validators=('isInt',),
    ),
))

RoundAboutImageSchema['title'].storage = atapi.AnnotationStorage()
RoundAboutImageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RoundAboutImageSchema, folderish=True, moveDiscussion=False)

class RoundAboutImage(folder.ATFolder):
    """RoundAbout Image"""
    
    security = ClassSecurityInfo()

    implements(IRoundAboutImage)

    portal_type = "RoundAbout Image"
    schema = RoundAboutImageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    tiles = []
    
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

atapi.registerType(RoundAboutImage, PROJECTNAME)
