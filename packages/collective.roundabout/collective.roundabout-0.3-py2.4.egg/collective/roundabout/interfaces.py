from zope import schema
from zope.interface import Interface

class IRoundAboutMapHotspot(Interface):
    """RoundAbout Map Hotspot"""

class IRoundAboutMap(Interface):
    """RoundAbout Map"""

class IRoundAboutImageHotspot(Interface):
    """RoundAbout Image Hotspot"""

class IRoundAboutImage(Interface):
    """RoundAbout Image"""

class IRoundAboutTour(Interface):
    """Container for RoundAbout images and maps."""
