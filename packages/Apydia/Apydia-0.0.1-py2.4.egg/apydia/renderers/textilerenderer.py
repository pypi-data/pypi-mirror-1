
from apydia.renderers.base import HTMLRenderer

from textile import textile


class TextileRenderer(HTMLRenderer):
    name = "textile"
    
    def _render(self, source):
        return textile(source)

    def render_description(self, desc):
        """ render full description (without title) """
        return self._render(desc.docstring)
    
    def render_short_desc(self, desc):
        """ render first paragraph (without title) """
        return self._render(desc.docstring)
    
    def render_title(self, desc):
        """ render title only """
        return self._render(desc.docstring[0:1])
