
from paste.script.templates import var, Template, paste_script_template_renderer

class DistCmdPackage(Template):

    _template_dir = 'distcmd_package'
    summary = "A disthelper-based package for setup.py commands"
    vars = [
        var('command', 'Name of setup.py command'),
        var('description', 'One-line description of the command'),
        # var('long_description', 'Multi-line description (in reST)'),
        ]

    template_renderer = staticmethod(paste_script_template_renderer)