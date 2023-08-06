from plone.app.layout.viewlets.common import ViewletBase
from zope.interface import implements, Interface
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize

class IPanoramaStarter(Interface):
    """
    """
    def genJSPanoramaCode(self, **kw):
        """
        """



class PanoramaStarter(ViewletBase):
    """
    """
    implements(IPanoramaStarter)

    def update(self):
        """
        """

    @memoize
    def panorama_available(self):
        """ Only activate the panorama viewlet if inqbus.plone.panorama is installed in this site.
        """
        pqinstaller = getToolByName(self.context, "portal_quickinstaller")
        installed_products_ids = [iprod['id'] for iprod in pqinstaller.listInstalledProducts()]
        if 'inqbus.plone.panorama' in installed_products_ids:
            return True
        else:
            return False

    def get_panorama_properties(self):
        """
        """
        propSheet = getToolByName(self.context, "portal_properties")
        prop = 'inqbus_plone_panorama_properties'

        panorama_properties   = {}
        if hasattr(propSheet, prop):
            panorama_properties.update(dict(propSheet[prop].propertyItems()))

        return panorama_properties

    def gen_panorama_js(self, **kw):
        """
        """
        JSCode = """
        <script type="text/javascript">
            jq(document).ready(function(){
                jq("img.panorama").panorama({
                        viewport_width: %s,
                        speed: %s,
                        direction: '%s',
                        control_display: '%s',
                        start_position: %s,
                        auto_start: %s,
                        mode_360: %s,
                        loop_180: %s
                     });
            });
            
        </script>
        """
        panorama_properties = self.context.get_panorama_properties() 
        
        viewport_width = panorama_properties.get('viewport_width', '500')
        if not viewport_width:
            viewport_width = "500"

        speed = panorama_properties.get('speed', '30000')
        if not speed:
            speed = "30000"

        direction = panorama_properties.get('direction', 'left')
        if not direction:
            direction = "left"

        control_display = panorama_properties.get('control_display', 'auto')
        if not control_display:
            control_display = "500"

        start_position = panorama_properties.get('start_position', "0")
        if not start_position:
            start_position = "0"

        auto_start = panorama_properties.get('auto_start', True)
        if auto_start:
            auto_start = "true"
        else:
            auto_start = "false"

        mode_360 = panorama_properties.get('mode_360', False)
        if mode_360:
            mode_360 = "true"
        else:
            mode_360 = "false"
            
        loop_180 = panorama_properties.get('loop_180', True)
        if loop_180:
            loop_180 = "true"
        else:
            loop_180 = "false"

        JSCode = JSCode % (viewport_width, speed, direction, control_display, start_position, auto_start, mode_360, loop_180)



        return JSCode
