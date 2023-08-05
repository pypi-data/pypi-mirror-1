"""
    Markdown Renderer
    =================
    
    The markdown/Pygments code highlighting integration is a stripped down
    version of "CodeHilite" which can be found at
    http://achinghead.com/markdown/codehilite/ .
"""

import re
from apydia.renderers.base import HTMLRenderer
from markdown import Markdown, Preprocessor

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.util import ClassNotFound


__all__ = ["MarkdownRenderer"]


class Highlighter(object):
    lang_detect = re.compile(r"""
        (?:(?:::+)|(?P<shebang>[#]!))
        (?P<path>(?:/\w+)*[/ ])?
        (?P<lang>\w*)
    """, re.VERBOSE)
    
    def __init__(self, text):
        self.text = text
        self.formatter = HtmlFormatter(cssclass="source")
        self.lang = None
        
        lines = self.text.splitlines()
        first_line = lines.pop(0)
        matches = self.lang_detect.search(first_line)
        if matches:
            try:
                self.lang = matches.group("lang").lower()
            except IndexError:
                pass
            if matches.group("path"):
                lines.insert(0, first_line)
        else:
            lines.insert(0, first_line)
        self.text = "\n".join(lines).strip("\n")
    
    def highlight(self):
        if self.lang:
            lexer = get_lexer_by_name(self.lang)
        else:
            try:
                lexer = guess_lexer(self.text)
            except ClassNotFound:
                lexer = get_lexer_by_name("text")
        return highlight(self.text, lexer, self.formatter)


class MarkdownRenderer(HTMLRenderer):
    name = "markdown"
    
    def __init__(self):
        self.markdown = md = Markdown(safe_mode=False)
        
        def _highlight_block(parent_elem, lines, in_list):
            detabbed, rest = md.blockGuru.detectTabbed(lines)
            text = "\n".join(detabbed).rstrip() + "\n"
            code = Highlighter(text)
            placeholder = md.htmlStash.store(code.highlight())
            parent_elem.appendChild(md.doc.createTextNode(placeholder))
            md._processSection(parent_elem, rest, in_list)
        self.markdown._processCodeBlock = _highlight_block
    
    def _render(self, source):
        if not source:
            return u""
        return self.markdown.__str__(source)
