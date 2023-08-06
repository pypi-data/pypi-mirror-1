from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer bound to a Skin
       Selection in portal_skins.
       If you need to register a viewlet only for the "Web Couturier iCompany Theme"
       skin, this is the interface that must be used for the layer attribute
       in webcouturier.icompany.theme/browser/configure.zcml.
    """
    
class ISubmenuViewlet(Interface):
    """ Marker interface.
        Allows to render menu of sublevels with depth = 1 for current
        section. Renders as a submenu in global navigation.
    """

    def getSubmenu(self, selected_id=''):
        """Get the submenu tree for selected tab"""