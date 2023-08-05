import pkg_resources
from turbogears.widgets import Widget
from turbogears.widgets import CSSLink, JSLink, register_static_directory
from scriptaculous.widgets import prototype_js, scriptaculous_js

__all__ = ['lightwindow_js', 'lightwindow_css', 'LightWindow', 'lightwindow']

pkg_path = pkg_resources.resource_filename(__name__, "static")
register_static_directory("TGLightWindow", pkg_path)

lightwindow_js = JSLink("TGLightWindow", "javascript/lightwindow.js")
lightwindow_css = CSSLink("TGLightWindow", "css/lightwindow.css")

class LightWindow(Widget):
    css             = [lightwindow_css]
    javascript      = [prototype_js, scriptaculous_js, lightwindow_js]

lightwindow = LightWindow()
