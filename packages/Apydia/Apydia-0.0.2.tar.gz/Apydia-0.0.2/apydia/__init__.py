"""
    Apydia - Python API Reference Generator
    =======================================
    
    Apydia is an API reference documentation generator for Python. It's
    designed as an instantly serviceable replacement for Pudge's
    API-documentation generator. It won't generate complete websites from
    reST etc. like Pudge does, though - Apydia is only about the API.
    
    Features currently include:
    ---------------------------
    
    - Basic [Pudge](http://pudge.lesscode.org/ "Pudge") compatibility and a short and easy migration path
    - Rudimentary Trac-integration, that is links into Trac's sourcecode browser
    - Some fair amount of usability
    - Setuptools integration
    - Flexible, [Genshi/XInclude](http://genshi.edgewall.org/ "Genshi - Trac")-based themeability with theme inheritance
    - Support for various text formats like [Markdown](http://daringfireball.net/projects/markdown/ "Daring Fireball: Markdown"), [Textile](http://www.textism.com/tools/textile/ "Textism: Tools: Textile") and [reST](http://docutils.sourceforge.net/ "Docutils: Documentation Utilities")
    - Other parsers can easily be plugged in on demand
    - Syntax highlighting thanks to [Pygments](http://pygments.org/ "Pygments &mdash; Python syntax highlighter")
    
    Planned features are:
    ---------------------
    
    - JavaScript-based live search (clientside index, no AJAX)
    - Maybe a couple more themes
"""

__docformat__ = "markdown"
