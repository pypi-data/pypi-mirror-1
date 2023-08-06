
import traceback
import textwrap
import os
import tokenize
import pkg_resources
from paste.script import copydir
from paste.script.command import Command
from paste.script.create_distro import CreateDistroCommand
from textwrap import dedent
import compiler
import compiler.ast
from setuptools import find_packages

class DistCmd(CreateDistroCommand):

    usage = 'COMMAND [package=NAME VAR1=VALUE1 ...]'
    summary = "Creates a custom setup.py command"
    short_description = summary

    description = """\
    Creates a custom distutils based setup.py command and adds it to your Python distribution.
    """

    parser = Command.standard_parser(
        simulate=True, no_interactive=True, quiet=True, overwrite=True)
    parser.add_option('-t', '--template',
                      dest='templates',
                      metavar='TEMPLATE',
                      action='append',
                      help="Add a template to the create process")
    parser.add_option('-o', '--output-dir',
                      dest='output_dir',
                      metavar='DIR',
                      default='.',
                      help="Put the directory into DIR (default current directory)")
    parser.add_option('--list-templates',
                      dest='list_templates',
                      action='store_true',
                      help="List all templates available")
    parser.add_option('--list-variables',
                      dest="list_variables",
                      action="store_true",
                      help="List all variables expected by the given template (does not create a package)")
    parser.add_option('--check',
                      dest='check',
                      action='store_true',
                      help="Checks integrity of the command.  Assumes you've already created the command")
    _default_opt = 'distcmds'
    parser.add_option('--distcmds-mod',
                      help=(
                        "Submodule to put commands in.  Defaults to '%s',  For example, when adding a setup.py "
                        "command named build_docs to project foo, it will go in foo.distcmds.build_docs" % _default_opt),
                      default=_default_opt)
    default_verbosity = 1
    default_interactive = 1
    
    def command(self):
        if self.options.list_templates:
            return self.list_templates()
        asked_tmpls = self.options.templates or ['distcmd']
        templates = []
        for tmpl_name in asked_tmpls:
            self.extend_templates(templates, tmpl_name)
        if self.options.list_variables:
            return self.list_variables(templates)
        if self.verbose:
            print 'Selected and implied templates:'
            max_tmpl_name = max([len(tmpl_name) for tmpl_name, tmpl in templates])
            for tmpl_name, tmpl in templates:
                print '  %s%s  %s' % (
                    tmpl_name, ' '*(max_tmpl_name-len(tmpl_name)),
                    tmpl.summary)
            print
        if not self.args:
            if self.interactive:
                command = self.challenge('Enter name of command')
            else:
                raise BadCommand('You must provide a COMMAND')
        else:
            command = self.args[0].strip()
        command = self._bad_chars_re.sub('', command.lower())

        templates = [tmpl for name, tmpl in templates]
        output_dir = self.options.output_dir
        
        vars = {'command': command,
                'distcmds_mod': self.options.distcmds_mod}
        vars.update(self.parse_vars(self.args[1:]))
        
        found_setup=False
        if os.path.exists(os.path.join(output_dir, 'setup.py')):
            found_setup=True
        if 'package' not in vars:
            if self.interactive:
                vars['package'] = None
                if found_setup:
                    try:
                        vars['package'] = find_mod_in_setup(
                            open(os.path.join(output_dir, 'setup.py'),'r').read(),
                            output_dir)
                    except Exception, exc:
                        if self.verbose:
                            print "find_mod_in_setup: %s: %s" % (exc.__class__.__name__, exc)
                if vars['package'] is None:
                    vars['package'] = self.challenge('Enter package name')
            else:
                raise BadCommand('You must specify package=NAME')
        pkg_name = self._bad_chars_re.sub('', vars['package'].lower())
        pkg_dir = os.path.join(output_dir, pkg_name)
        
        if not found_setup:
            self.create_setup_file(output_dir, vars)
        
        if self.verbose: # @@: > 1?
            self.display_vars(vars)

        if self.options.check:
            self.check_command(output_dir, templates, vars)
            return
        if not os.path.exists(pkg_dir):
            # We want to avoid asking questions in copydir if the path
            # doesn't exist yet
            copydir.all_answer = 'y'
            

        # First we want to make sure all the templates get a chance to
        # set their variables, all at once, with the most specialized
        # template going first (the last template is the most
        # specialized)...
        for template in templates[::-1]:
            vars = template.check_vars(vars, self)
            
        for template in templates:
            self.create_template(
                template, output_dir, vars)

        if self.verbose:
            print "patching %s ..." % os.path.join(output_dir, 'setup.cfg')
        self.write_vars(os.path.join(output_dir, 'setup.cfg'), 
                        {'command_packages': '%s.%s' % (pkg_name, self.options.distcmds_mod)},
                                section='global')
        
        print 
        print (os.path.join(pkg_dir, self.options.distcmds_mod, command) + '.py')
        print "...is ready to edit"
        print "run as:"
        print "    python setup.py %s" % command
        print
        
    def all_entry_points(self):
        if not hasattr(self, '_entry_points'):
            self._entry_points = list(pkg_resources.iter_entry_points(
            'disthelper.distcmd_templates'))
        return self._entry_points
    
    def check_command(self, output_dir, templates, vars):
        # use the templates to check instead?
        ok=True
        pkg_dir = os.path.join(output_dir, vars['package'])
        if not os.path.exists(pkg_dir):
            ok=False
            print "package %s does not exist" % pkg_dir
            print "re-run distcmd"
        distcmds_mod = os.path.join(output_dir, vars['package'], vars['distcmds_mod'])
        if not os.path.exists(distcmds_mod):
            ok=False
            print "distcmds_mod %s does not exist" % distcmds_mod
            print "re-run distcmd"
        cmd_mod = os.path.join(distcmds_mod, "%s.py" % vars['command'])
        if not os.path.exists(cmd_mod):
            ok=False
            print "cmd_mod %s does not exist" % cmd_mod
            print "re-run distcmd"
        cmd_mod_path = ".".join([vars['package'], vars['distcmds_mod'], vars['command']])
        print "attempting to import %s" % cmd_mod_path
        try:
            __import__(cmd_mod_path, globals(), globals(), ['__name__'])
        except:
            traceback.print_exc()
            ok=False
            print
        else:
            print "OK"
        setup_cfg = os.path.join(output_dir, 'setup.cfg')
        if not os.path.exists(setup_cfg):
            ok=False
            print "%s does not exist" % setup_cfg
            print "re-run distcmd"
        else:
            if self.verbose:
                print "checking vars in %s" % setup_cfg
            conf = self.read_vars(setup_cfg, section='global')
            if 'command_packages' not in conf:
                ok=False
                print "%s does not declare command_packages" % setup_cfg
                print "re-run distcmd"
            else:
                distcmds_mod_path = ".".join([vars['package'], vars['distcmds_mod']])
                if distcmds_mod_path not in conf['command_packages']:
                    ok=False
                    print "%s not in command_packages" % distcmds_mod_path
                    print "re-run distcmd"
        print
        if ok:
            print "%s OK" % vars['command']
        else:
            self.return_code = 1
            print "%s ERRORS" % vars['command']
    
    def create_setup_file(self, output_dir, vars):
        setup = os.path.join(output_dir, 'setup.py')
        print "** creating %s (you'll probably need to edit this)" % setup
        f = open(setup, 'w')
        svars = vars.copy()
        svars['packages'] = [vars['package'], ".".join([vars['package'], vars['distcmds_mod']])]
        f.write(textwrap.dedent("""
            try:
                from setuptools import setup, find_packages
                extra_kw = dict(
                    packages=find_packages(),
                    install_requires=[],
                    tests_require=[])
            except ImportError:
                from distutils.core import setup
                extra_kw = dict(packages=%(packages)r)
                
            setup(
                name="%(package)s",
                description="",
                long_description="",
                url="",
                author="",
                author_email="",
                **extra_kw
            )""" % svars))
        f.close()
        
    def inspect_files(self, output_dir, templates, vars):
        raise NotImplementedError("inspecting files")
        # return super(DistCmd, self).inspect_files(output_dir, templates, vars)
                                
    def extend_templates(self, templates, tmpl_name):
        if '#' in tmpl_name:
            dist_name, tmpl_name = tmpl_name.split('#', 1)
        else:
            dist_name, tmpl_name = None, tmpl_name
        if dist_name is None:
            for entry in self.all_entry_points():
                if entry.name == tmpl_name:
                    tmpl = entry.load()(entry.name)
                    dist_name = entry.dist.project_name
                    break
            else:
                raise LookupError(
                    'Template by name %r not found' % tmpl_name)
        else:
            dist = pkg_resources.get_distribution(dist_name)
            entry = dist.get_entry_info(
                'disthelper.distcmd_templates', tmpl_name)
            tmpl = entry.load()(entry.name)
        full_name = '%s#%s' % (dist_name, tmpl_name)
        for item_full_name, item_tmpl in templates:
            if item_full_name == full_name:
                # Already loaded
                return
        for req_name in tmpl.required_templates:
            self.extend_templates(templates, req_name)
        templates.append((full_name, tmpl))

class SetupVisitor(object):
    def __init__(self):
        self.mods = []
        self.find_packages_spec = None
        self.list_attr = (
            'py_modules',
            'packages'
        )
        self.stop = False
    
    # def __getattr__(self, name):
    #     print name
    #     raise AttributeError('no %s' %name)

    def default(self, node):
        for child in node.getChildNodes():
            self.visit(child)
            if self.stop:
                return
    
    def visitCallFunc(self, node):
        if node.node.name == 'setup':
            for child in node.getChildNodes():
                if child.name in self.list_attr:
                    children = child.getChildNodes()
                    if isinstance(children[0], compiler.ast.List):
                        const = children[0].getChildNodes()
                    elif (  isinstance(children[0], compiler.ast.CallFunc) 
                            and children[0].node.name=='find_packages'):
                        self.find_packages_spec = []
                        for arg in children[0].args:
                            if isinstance(arg, compiler.ast.Keyword) and arg.name=='exclude':
                                clist = arg.getChildNodes()[0]
                                self.find_packages_spec = [a.value for a in clist]
                        break
                    else:
                        raise RuntimeError("unexpected node: %s" % children[0].__class__)
                    self.mods = [c.value for c in const]
                    break
            self.stop = True

def unique_mod_list(modlist):
    """turns ['foo', 'foo.submodule', 'foo.another'] into ['foo']"""
    umods = []
    for m in modlist:
        mod = m.split('.')[0]
        if mod not in umods:
            umods.append(mod)
    return umods
    
def find_mod_in_setup(setup_fileobj, project_path):
    """takes the string contents of a setup.py file and tries to guess the module name.
    
    if the setup.py employs setuptools.find_packages(), this will be used along 
    project_path, the same way.
    
    if no module is found or multiple modules are found, returns None
    """
    ast = compiler.parse(setup_fileobj)
    psetup = SetupVisitor()
    compiler.visitor.walk(ast, psetup)
    if not psetup.mods and psetup.find_packages_spec is not None:
        exclude = psetup.find_packages_spec
        psetup.mods = find_packages(where=project_path, exclude=exclude)
    psetup.mods = unique_mod_list(psetup.mods)
    if len(psetup.mods) == 1:
        return psetup.mods[0]
    else:
        return None
            
        