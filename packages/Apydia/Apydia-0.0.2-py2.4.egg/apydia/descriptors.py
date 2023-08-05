"""
    Descriptors
    ===========
    
    Descriptors represent and describe the target project's class- and
    module-model internally. They provide methods to extract information
    about the objects in more or less intelligent ways.
"""

import logging
import sys
from os.path import split
from inspect import ismodule, isclass, isfunction, ismethod, isbuiltin, \
                    getmodule, getsourcefile, findsource, getdoc, \
                    getcomments, getargspec, formatargspec

import pkg_resources
from glob import glob

__all__ = ["create_desc"]

log = logging.getLogger(__name__)


def get_distribution():
    """
        Returns the pkg_resources' distribution rooted in the current
        directory.
    """
    try:
        dist_name = glob("*.egg-info")[0][:-9]
    except IndexError:
        dist_name = None
    if dist_name:
        return pkg_resources.get_distribution(dist_name)


def _getsourcefile_relative(obj):
    """
        Returns the relative filename in respect to the project root
        (ie. the root module's home).
    """
    
    def root_module_basedir(module):
        module = getmodule(module)
        if "." in module.__name__:
            module = sys.modules[module.__name__.split(".")[0]]
            return split(getsourcefile(module))[0]
        else:
            return split(getsourcefile(module))[0]
    
    try:
        # try to figure out basedir through distribution (thanks to Alberto)
        dist = get_distribution()
        if dist:
            base = dist.location
        else:
            base = root_module_basedir(obj)
        absolute_path = getsourcefile(obj)
        log.debug("base: %r, abspath: %r", base, absolute_path)
        return absolute_path[len(base):]
    except (TypeError, AttributeError):
        return ""


def _getcomments(value):
    comment = getcomments(value)
    if comment:
        indent = sys.maxint
        # strip hashes and leading spaces
        comment = [line.lstrip().lstrip("#") for line in comment.split("\n")]
        for line in comment:
            s = line.lstrip()
            if s: indent = min(indent, len(line) - len(s))
        if indent < sys.maxint:
            return "\n".join(line[indent:] for line in comment)
    return comment


class Descriptor(object):
    """ Descriptor baseclass """
    
    represents = "Object"
    matches = staticmethod(lambda v:True) # match anything
    instances = dict()
    
    def __init__(self, value):
        try:
            Descriptor.instances[value] = self
        except TypeError:
            pass
        
        self.value = value
        try:
            self.pathname = getattr(value, "__name__", "")
        except:
            self.pathname = ""
        if not isinstance(self.pathname, basestring):
            self.pathname = ""

        try:
            self.name = self.pathname.rsplit(".", 1)[-1]
        except TypeError:
            self.name = ""
        self.parent = None
        
        self.file = _getsourcefile_relative(value)
        self._members = self.find_members()
        
        try:
            self.line = findsource(value)[1]
        except (TypeError, IOError):
            self.line = 0 # TODO: how to determine linenumbers for attrs?
        
        self.type = type(self).__name__.lower()
        if self.type.endswith("desc"):
            self.type = self.type[:-4]
        
        # TODO: remove "-*- coding: ... -*-"
        self.docstring = getdoc(value) or _getcomments(value) or ""        
    
    # TODO: introduce additional, local member names?
    def generate_memberlist(self, type_=None):
        for name, member in self._members.iteritems():
            if member.name == "<lambda>":
                member.name = name
            if not type_ or (type_ and type(member) is type_):
                yield member
    
    def contains(self, item):
        if isinstance(item, ClassDesc):
            return item.module.pathname == self.pathname
        elif item.pathname == self.pathname:
            return True
        return False
    
    # TODO: make this flexible to be able link to svn repos and whatever
    def sourcelink(self, project=None):
        try:
            baseurl = project.options.trac_browser_url
            if baseurl:
                return "%s%s#L%s" % (baseurl, self.file, self.line)
        except AttributeError:
            pass
        return ""
    
    # Useful properties
    # ------------------------------------------------------------------------
    
    @property
    def href(self):
        return "%s.html" % self.pathname
    
    @property
    def path(self):
        if self.parent:
            return self.parent.path + [self]
        else:
            return [self]

    @property
    def docformat(self):
        try:
            docformat = getattr(self.value, "__docformat__", None)
        except:
            docformat = None
        if not docformat and self.parent and self.parent != self:
            return self.parent.docformat
        elif isinstance(docformat, basestring):
            return docformat.split()[0]
        else:
            return docformat
    
    # Shortcuts
    # ------------------------------------------------------------------------
    
    modules = property(lambda self:sorted(self.generate_memberlist(ModuleDesc)))
    classes = property(lambda self:sorted(self.generate_memberlist(ClassDesc)))
    functions = property(lambda self:sorted(self.generate_memberlist(FunctionDesc)))
    methods = property(lambda self:sorted(self.generate_memberlist(MethodDesc)))
    attributes = property(lambda self:sorted(self.generate_memberlist(AttributeDesc)))
    members = property(lambda self:sorted(self.generate_memberlist()))
    
    # Helpers
    # ------------------------------------------------------------------------
    
    def find_members(self):        
        """
            This method is to be overridden by subclasses, which will
            return an individual list of members
        """
        return dict()
    
    def exported_keys(self):
        for name in ("__doc_all__", "__pudge_all__", "__all__"):
            keys = getattr(self.value, name, None)
            if isinstance(keys, list):
                return keys
        return None
    
    def __cmp__(self, other):
        return cmp(self.name, other.name)


class ModuleDesc(Descriptor):
    """ Descriptor for a module """
    
    represents = "Module"
    matches = staticmethod(ismodule)
    
    _modules = dict()
    
    def __init__(self, module):
        super(ModuleDesc, self).__init__(module)
        self.line = 1
        
        # add submodules as members
        for name, desc in self.find_submodules():
            if name not in self._members:
                self._members[name] = desc
        
        ModuleDesc._modules[self.pathname] = self
        
        if "." in self.pathname:
            self.parent = ModuleDesc.load(".".join(self.pathname.split(".")[:-1]))
    
    @classmethod
    def load(cls, pathname):
        if pathname not in cls._modules:
            try:
                __import__(pathname)
            except ImportError:
                pass
            return create_desc(sys.modules[pathname])
        else:
            return cls._modules[pathname]
    
    def find_members(self):
        exported_keys = self.exported_keys()
        keys = dir(self.value)
        
        if exported_keys:
            keys = [key for key in keys if key in exported_keys]
        elif exported_keys is None:
            d = self.value.__dict__
            def gen_keys(keys):
                for key in keys:
                    if not key.startswith("_"):
                        m = getmodule(d[key])
                        if m in (None, self.value):
                            yield key
            keys = list(gen_keys(keys))
        else:
            keys = []
        
        members = dict()
        for key in keys:
            value = getattr(self.value, key, None)
            module = getmodule(value)
            if value is not self.value:
                desc = create_desc(value)
                if not desc.parent and not isinstance(desc, ModuleDesc):
                    desc.parent = self
                    desc.pathname = ".".join([self.pathname, key])
                    desc.name = key
                    desc.file = self.file
                members[key] = desc
        return members
    
    def find_submodules(self):
        prefix = self.pathname + "."
        for module in filter(None, sys.modules.itervalues()):
            name = module.__name__
            if name.startswith(prefix) and "." not in name[len(prefix):]:
                m = ModuleDesc.load(name)
                yield m.name, m
    
    def module_tree(self, modules=[]):
        if self in modules:
            return modules
        
        modules = set(self.modules)
        for module in self.modules:
            modules.update(module.module_tree(modules))
        return modules
    
    @property
    def details(self):
        return self.href


class ClassDesc(Descriptor):
    """ Descriptor for a class """
    
    represents = "Class"
    matches = staticmethod(isclass)
    
    def __init__(self, class_):
        super(ClassDesc, self).__init__(class_)
        self.name = getattr(class_, "__name__", "")
        if not isinstance(self.name, basestring):
            self.name = ""
        self.module = ModuleDesc.load(getmodule(class_).__name__)
        self.parent = self.module
        self.pathname = ".".join([self.module.pathname, self.name])
    
    def find_members(self):
        exported_keys = self.exported_keys()
        keys = dir(self.value)
        if exported_keys:
            keys = [key for key in keys if key in exported_keys]
        elif exported_keys is None:
            keys = [key for key in keys if not key.startswith("_")]
        else:
            keys = []
        results = dict()
        for key in keys:
            try:
                value = getattr(self.value, key)
                desc = create_desc(value)
                desc.parent = self
                results[key] = desc
            except:
                pass
        return results
    
    @property
    def details(self):
        return self.href


class AttributeOrMethodDesc(Descriptor):
    """ Descriptor-baseclass for methods, functions and attributes """
    
    represents = "AttributeOrMethod"
    
    @property
    def href(self):
        return "%s.html#%s" % (self.parent.pathname, self.anchor)
    
    @property
    def anchor(self):
        return "%s-%s" % (self.type, self.name)


class AttributeDesc(AttributeOrMethodDesc):
    """ Descriptor for an attribute """
    
    represents = "Attribute"
    
    def __init__(self, value, *args, **kwargs):
        super(AttributeDesc, self).__init__(value, *args, **kwargs)
        self.docstring = _getcomments(value) or ""
    
    @property
    def fulltype(self):
        mytype = type(self.value)
        return ".".join([getmodule(mytype).__name__, mytype.__name__])


class FunctionDesc(AttributeOrMethodDesc):
    """ Descriptor for a function """
    
    represents = "Function"
    matches = staticmethod(isfunction)
    
    def __init__(self, function):
        super(FunctionDesc, self).__init__(function)
        self.name = function.__name__
        self.module = ModuleDesc.load(getmodule(function).__name__)
        self.parent = self.module
        self.pathname = ".".join([self.module.pathname, self.name])
        self.argspec = formatargspec(*getargspec(function))


class MethodDesc(FunctionDesc):
    """ Descriptor for a method """
        
    represents = "Method"
    matches = staticmethod(ismethod)


def create_desc(value):
    """
        This function returns the descriptor for the given ``value``. If there
        is none it will create it.
    """
    
    try:
        if value in Descriptor.instances:
            return Descriptor.instances[value]
    except TypeError: # "unhashable"
        return AttributeDesc(value)
    
    for class_ in [ModuleDesc, ClassDesc, MethodDesc, FunctionDesc]:
        if class_.matches(value):
            return class_(value)
    return AttributeDesc(value)
