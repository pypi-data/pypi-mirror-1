from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.portlets.interfaces import IColumn

class IThemeSchools(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IThemeSchoolsPortlets(IColumn):
    """Add top portlets manager
    """