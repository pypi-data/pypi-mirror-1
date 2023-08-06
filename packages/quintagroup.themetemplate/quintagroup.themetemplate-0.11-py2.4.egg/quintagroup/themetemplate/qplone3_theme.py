import os
import copy
import datetime

from zopeskel.plone3_theme import Plone3Theme
from zopeskel.base import get_var
from zopeskel.base import var

class qPlone3Theme(Plone3Theme):
    _template_dir = 'templates/qplone3_theme'
    summary = "A Quinta Group Theme for Plone 3.0 with nested namespace"
    required_templates = ['plone_app']
    use_cheetah = True
    use_local_commands = True

    vars = copy.deepcopy(Plone3Theme.vars)
    get_var(vars, 'namespace_package').default = 'quintagroup'
    get_var(vars, 'namespace_package').description = 'Namespace package (like quintagroup)'
    get_var(vars, 'author').default = 'Quintagroup'
    get_var(vars, 'author_email').default = 'skins.develop.group@quintagroup.com'
    get_var(vars, 'keywords').default = get_var(vars, 'keywords').default + ' quintagroup'
    get_var(vars, 'url').default = 'http://svn.quintagroup.com/skins'
    get_var(vars, 'package').default = 'example'
    get_var(vars, 'description').default = 'An installable Quintagroup theme for Plone 3'
    get_var(vars, 'version').default = '0.1'
    vars.insert(1, var('namespace_package2',
                        'Nested namespace package (like theme)',
                        default='theme'))

    def pre(self, command, output_dir, vars):
        vars['timestamp'] = datetime.date.today().strftime("%Y%m%d")
        super(qPlone3Theme, self).pre(command, output_dir, vars)

    def post(self, command, output_dir, vars):
        np2, np = vars['namespace_package2'], vars['namespace_package']
        p = vars['package']
        sdir = os.path.join(output_dir, np, np2, p, 'skins')

        # Prevent overriding passed config file
        # Result config will be written to same 
        # name file with '.result' postfix
        if command.options.config:
            command.options.config += '.result'
