"""
    Generator
    =========

    The ``Generator``-class is responsible for rendering X/HTML-files,
    writing out dynamically generated resources, like css-files for syntax
    highlighting, creating the directory tree and copying all static files
    that are specified in the theme's ``theme.ini``-file.
"""

import logging

from os import makedirs, listdir
from os.path import join, dirname, isdir
from shutil import copy

from genshi.template import TemplateLoader

from pygments.formatters import HtmlFormatter

from apydia.descriptors import *
from apydia import helpers

log = logging.getLogger(__name__)

__all__ = ["Generator"]


class Generator(object):
    
    """
        The ``Generator`` class, which is responsible for rendering and
        copying HTML-files and needed resources.
    """
    
    def __init__(self, project):
        self.project = project
        self.options = project.options
        self.generated = set()
        self.loader = TemplateLoader(project.theme.template_dirs)
    
    def generate(self, desc):
        """ Generate all HTML for a given descriptor and it's members. """
        if desc in self.generated:
            return
        
        if not helpers.is_included(desc.pathname, self.options):
            return
        
        log.debug("generating \"%s\"", self.target_filename(desc))
        
        self.generated.add(desc)
        
        for generator in (desc.modules, desc.classes):
            for member in generator:
                self.generate(member)
        
        data = dict(
            project = self.project,
            desc = desc,
            options = self.options,
            helpers = helpers
        )
        
        template = self.loader.load("%s.html" % desc.type)
        stream = template.generate(**data)
        outfile = file(self.target_filename(desc), "w")
        try:
            outfile.write(stream.render(self.options.format))
        finally:
            outfile.close()
    
    def generate_resources(self):
        """ Currently just creates the CSS file for syntax highlighting.  """
        pygments_style = self.project.theme.pygments_style
        pygments_style_css = self.project.theme.pygments_style_css
        css = HtmlFormatter(style=pygments_style).get_style_defs(".source")
        filename = join(self.options.destination, pygments_style_css)
        log.debug("generating \"%s\"", filename)
        
        outfile = file(filename, "w")
        try:
            outfile.write(css)
        finally:
            outfile.close()
        
    
    def create_dirs(self):
        """ Creates the target directory where all content goes. """
        if not isdir(self.options.destination):
            log.debug("creating directory \"%s\"", self.options.destination)
            makedirs(self.options.destination)
    
    def copy_resources(self):
        """ Copies all required files like CSS, JavaScipts and images. """
        project, theme = self.project, self.project.theme
        
        for resource, relative in theme.resources:
            destpath = join(self.options.destination, relative)
            dir = dirname(destpath)
            if not isdir(dir):
                log.debug("creating directory \"%s\"", dir)
                makedirs(dir)
            log.debug("copying \"%s\" to \"%s\"", resource, destpath)
            
            copy(resource, destpath)
    
    def target_filename(self, desc):
        """
            Returns the full path and filename for the file that will be
            generated for the descriptor given by ``desc``.
        """
        return join(self.options.destination, desc.href)

