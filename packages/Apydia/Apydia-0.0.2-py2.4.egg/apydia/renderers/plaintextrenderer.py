from apydia.renderers.base import Renderer


class PlainTextRenderer(Renderer):
    name = ["plain", "plaintext", "text"]
    
    def _render(self, source):
        return "<pre>%s</pre>" % source
