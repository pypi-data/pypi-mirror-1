import sys
from distutils import log
from distutils.cmd import Command
from distutils.errors import *
class build_docs(Command):
    description = "builds docs"
    user_options = [('long-option=', 'l', '<help>'),
                    ('other-long-option', 'o', '<help>')]
    boolean_options = 'other-long-option'
    def initialize_options(self):
        self.long_option = None
        self.other_long_option = False
    def finalize_options(self):
        pass
        #raise DistutilsOptionError(...)
    def run(self):
        log.info("doing stuff...")