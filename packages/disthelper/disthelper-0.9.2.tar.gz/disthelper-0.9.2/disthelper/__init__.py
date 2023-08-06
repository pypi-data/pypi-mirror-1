
import re
import sys
from ConfigParser import ConfigParser
from optparse import OptionParser
from distutils import log
try:
    from setuptools import Command as _Command
except ImportError:
    from distutils.cmd import Command as _Command

from distutils.core import setup as _distutils_setup
try:
    from setuptools import setup as _setuptools_setup
except ImportError:
    _setuptools_setup = None
    
from distutils.dist import Distribution as _Distribution
_spec_assign = re.compile(r'\s*=\s*')

def load_entry_point_spec(spec, name=None):
    if name is None:
        parts = _spec_assign.split(spec)
        if len(parts) == 1:
            raise ValueError("invalid entry_point spec: %r (expected name = module.path:optional_object)" % spec)
        name, spec = parts
    if ':' in spec:
        mod, obj = spec.split(':')
    else:
        mod, obj = spec, None
    entry = __import__(mod, globals(),globals(), [obj])
    if obj is not None:
        if not hasattr(entry, obj):
            raise ImportError("attribute %s does not exist in module %s" % (obj, mod))
        return name, getattr(entry, obj)
    else:
        return name, entry

class Distribution(_Distribution):
    def __init__(self, attrs=None):
        _Distribution.__init__(self, attrs=attrs)
        filenames = self.find_config_files()
        for filename in filenames:
            parser = ConfigParser()
            parser.read(filename)
            for section in parser.sections():
                if section == 'disthelper:commands':
                    for item in parser.items(section):
                        name, spec = item
                        name, obj = load_entry_point_spec(spec, name=name)
                        obj = convert_optparse_to_legacy_opts(obj)
                        self.cmdclass[name] = obj

# def setup(**attrs):
#     attrs['distclass'] = Distribution
#     if _setuptools_setup is not None:
#         setup = _setuptools_setup
#     else:
#         setup = _distutils_setup
#     return setup(**attrs)

def convert_optparse_to_legacy_opts(cmd):
    if not hasattr(cmd, 'parser'):
        return cmd
        
    '''description = "builds docs"
        user_options = [('long-option=', 'l', '<help>'),
                        ('other-long-option', 'o', '<help>')]
        boolean_options = 'other-long-option' '''
    cmd._options_from_parser = []
    cmd.user_options = []
    cmd.boolean_options = []
    for opt in cmd.parser.option_list:
        if opt._long_opts == ['--help']:
            continue
        cmd._options_from_parser.append(opt)
        if len(opt._long_opts):
            # strip leading -- (this should be done more carefully)
            long_opt = opt._long_opts[0][2:]
            long_opt = '%s=' % long_opt
        else:
            long_opt = None
        if len(opt._short_opts):
            short_opt = opt._short_opts[0][1:] # ditto
        else:
            short_opt = None
        cmd.user_options.append((long_opt, short_opt, '<help>'))
        # add boolean_options
    return cmd

class Command(_Command):
    def __init__ (self, dist):
        _Command.__init__(self, dist)
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

        