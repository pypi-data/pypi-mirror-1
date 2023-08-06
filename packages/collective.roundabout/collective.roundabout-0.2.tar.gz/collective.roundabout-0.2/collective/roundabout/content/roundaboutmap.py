"""Definition of the RoundAbout Map content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *

from AccessControl import ClassSecurityInfo

from collective.roundabout import roundaboutMessageFactory as _
from collective.roundabout.interfaces import IRoundAboutMap
from collective.roundabout.config import PROJECTNAME

RoundAboutMapSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    ImageField(
        name='image',
        widget=PhotoField._properties['widget'](
            label="Image",
            description="Map image",
            label_msgid='label_map_image',
            description_msgid='description_map_image',
            i18n_domain='collective.roundabout',
        ),
        storage=AttributeStorage(),
        max_size=(768,768),
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
))

RoundAboutMapSchema['title'].storage = atapi.AnnotationStorage()
RoundAboutMapSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RoundAboutMapSchema, folderish=True, moveDiscussion=False)

class RoundAboutMap(folder.ATFolder):
    """RoundAbout Map"""

    security = ClassSecurityInfo()

    implements(IRoundAboutMap)

    portal_type = "RoundAbout Map"
    schema = RoundAboutMapSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(RoundAboutMap, PROJECTNAME)
