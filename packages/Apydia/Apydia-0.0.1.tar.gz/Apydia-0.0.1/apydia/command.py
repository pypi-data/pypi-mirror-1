"""
    Apydia command line tool (and distutils command)
    ------------------------------------------------
    
    Use the ``apydia`` command to generate API reference documentation:
    
        Usage: apydia [options] [modules]

        Apydia API Documentation Generator

        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -c CONFIGFILE, --config=CONFIGFILE
                                specify config file
          -d DESTINATION, --destination=DESTINATION
                                specify output directory
          -o, --open            open in browser
          -f FORMAT, --format=FORMAT
                                rendering format (xhtml or html, defaults to xhtml)
          -s THEME, --style=THEME
                                Choose a theme
          -p DOCFORMAT, --parser=DOCFORMAT
                                docstring parser (markdown, textile, restucturedtext,
                                html, ...)
          -b TRAC_BROWSER_URL, --trac-browser-url=TRAC_BROWSER_URL
                                trac browser url (path to root module)
          -q, --quiet           silent mode
          -t TITLE, --title=TITLE
                                title of project
          -x EXCLUDE_MODULES, --exclude-modules=EXCLUDE_MODULES
                                exclude modules

    
    Or run it through distutils by configuring your project's setup.cfg
    appropriately (see documentation) and issuing from your project root:
        
        python setup.py apydia
"""

import logging

from optparse import OptionParser

from apydia import release
from apydia.project import Project

import warnings

log = logging.getLogger(__name__)

__all__ = ["main", "apydia"]


# optional distutils integration
try:
    import distutils.cmd

    class apydia(distutils.cmd.Command):
        """
            ``apydia`` command
            ==================
            
            The ``apydia``-command as an extension to distutils.
            
            Run by typing
                
                python setup.py apydia
            
            
            Availlable options are:

                --title (-t)             The name of your project
                --destination (-d)       Target directory where the apidocs go
                --theme (-t)             Choose an Apydia theme
                --docformat              Set this to the docstring's format (eg. markdown,
                                       textile, reStrucuturedText)
                --format (-f)            XHTML or HTML, defaults to xhtml
                --modules                Include the given modules in documentation
                --exclude-modules (-x)   Don't generate documentation for the given modules
                --trac-browser-url (-b)  URL to Trac's sourcecode browser
                --open (-o)              Open generated files in browser when done
            
            
            It is recommended to supply options through an
            ``[apydia]``-section in the target project's ``setup.cfg``.
            See the documentation of the ``apydia.command`` module for
            more information.
        """
        
        description = "Generate API Reference Documentations using Apydia"
    
        user_options = [
            ("title=", "t", "The name of your project"),
            ("destination=", "d", "Target directory where the apidocs go"),
            ("theme=", "t", "Choose an Apydia theme"),
            ("docformat=", None, "Set this to the docstring's format (eg. markdown, textile, reStrucuturedText)"),
            ("format=", "f", "XHTML or HTML, defaults to xhtml"),
            ("modules=", None, "Include the given modules in documentation"),
            ("exclude-modules=", "x", "Don't generate documentation for the given modules"),
            ("trac-browser-url=", "b", "URL to Trac's sourcecode browser"),
            ("open", "o", "Open generated files in browser when done")
        ]
    
        #boolean_options = []
    
        def initialize_options(self):
            self.title = ""
            self.destination = "apydocs"
            self.theme = "default"
            self.docformat = ""
            self.format = "xhtml"
            self.modules = []
            self.exclude_modules = []
            self.trac_browser_url = ""
            self.open = False
    
        def finalize_options(self):
            self.ensure_string_list("modules")
            self.ensure_string_list("exclude_modules")
            self.ensure_string("title")
            self.ensure_string("theme")
            self.ensure_string("trac_browser_url")
        
        def run(self):
            def generate():
                project = Project(self)
                project.generate()
                if self.open and self.open.lower() in ('1', 'true', 'yes'):
                    project.open_in_browser()
            self.execute(generate, (), msg="Generating API reference documentation.")

except ImportError:
    warnings.warn("distutils not installed.")


# FIXME: docstring
def main():
    """
        Generate api reference documentation from the command line
        
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua.
        
            #!python
            class CodeExample(object):
                def __init__(self):
                    pass
        
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum.
    """
    
    optparser = OptionParser(
        usage = "%prog [options] [modules]",
        description = release.description,
        version = release.version
    )
    
    optparser.set_defaults(
        title = "",
        destination = "apydocs",
        theme = "default",
        verbose = True,
        open = False,
        format = "xhtml",
        docformat = "restructuredtext",
        modules = "",
        exclude_modules = "",
        trac_browser_url = "" 
    )
    
    optparser.add_option(
        "-c", "--config", dest="configfile",
        help="specify config file"
    )
    
    optparser.add_option(
        "-d", "--destination", dest="destination",
        help="specify output directory"
    )
    
    optparser.add_option(
        "-o", "--open", dest="open", action="store_true",
        help="open in browser"
    )
    
    optparser.add_option(
        "-f", "--format", dest="format",
        help="rendering format (xhtml or html, defaults to xhtml)"
    )
    
    optparser.add_option(
        "-s", "--style", dest="theme",
        help="Choose a theme"
    )
    
    optparser.add_option(
        "-p", "--parser", dest="docformat",
        help="docstring parser (markdown, textile, restucturedtext, html, ...)"
    )
    
    optparser.add_option(
        "-b", "--trac-browser-url", dest="trac_browser_url",
        help="trac browser url (path to root module)"
    )
    
    optparser.add_option(
        "-q", "--quiet", action="store_false", dest="verbose",
        help="silent mode"
    )
    
    optparser.add_option(
        "-t", "--title", dest="title",
        help="title of project"
    )
    
    optparser.add_option(
        "-x", "--exclude-modules", dest="exclude_modules",
        help="exclude modules"
    )
    
    (options, args) = optparser.parse_args()
    
    # update defaults from configfile
    if options.configfile:
        from ConfigParser import ConfigParser
        cfgparser = ConfigParser()
        cfgparser.read(options.configfile)        
        cfgopts = dict(cfgparser.items("apydia"))
        optparser.set_defaults(**cfgopts)
    
    # overwrite configfile options with commandline options
    (options, args) = optparser.parse_args()
    
    try:
        options.modules = [m.strip() for m in options.modules.split(",")] + args
    except AttributeError:
        optparser.print_help()
        return

    options.exclude_modules = [m.strip() for m in options.exclude_modules.split(",")
                                if m.strip()]
    
    logger_settings = dict(format="%(asctime)s %(levelname)-8s %(message)s")
    if options.verbose:
        logger_settings["level"] = logging.DEBUG
    logging.basicConfig(**logger_settings)
    
    project = Project(options)
    project.generate()
    
    if options.open:
        project.open_in_browser()

if __name__ == "__main__":
    main()

