"""
Local templates for the qplone3_theme
"""
import os
from ConfigParser import SafeConfigParser
from paste.script import pluginlib

from zopeskel.base import var
from zopeskel.localcommands import ZopeSkelLocalTemplate

class QThemeSubTemplate(ZopeSkelLocalTemplate):
    use_cheetah = True
    parent_templates = ['qplone3_theme']

    # Flag for use template composition
    compose = None
    compodir_pref = "_compo"
    # list of 2 item tuple -
    # (compotemplate_name, compo marker), for ex.:
    compo_template_markers = []
    # list vars names to add in theme_vars egg_info file
    shared_vars = []

    def template_dir(self):
        if self.compose:
            # Prepare
            self._template_dir = os.path.join( \
                self._template_dir + self.compodir_pref, \
                self.compose )

        return super(QThemeSubTemplate, self).template_dir()

    def pre(self, command, output_dir, vars):
        """ Get all previous template vars
        """
        for k, v in self.get_template_vars(output_dir, vars).items():
            if not k in vars.keys():
                vars[k] = v
        super(QThemeSubTemplate, self).pre(command, output_dir, vars)

    def post(self, command, output_dir, vars):
        """ Call write_files function for every subtemplate,
             - change marker name for every subtemplate,
             - set compose prop for change subtemplate path calculation
        """
        if self.compo_template_markers:
            for cname, cmarker in self.compo_template_markers:
                original_template_dir = self._template_dir
                self.compose = cname
                self.marker_name = cmarker
                self.write_files(command, output_dir, vars)
                self._template_dir = original_template_dir

        self.add_template_vars(output_dir, vars)
        super(QThemeSubTemplate, self).post(command, output_dir, vars)

    def get_template_vars(self, output_dir, vars):

        res = {}
        egg_info = pluginlib.find_egg_info_dir(output_dir)
        theme_vars_fp = os.path.join(egg_info, 'theme_vars.txt')

        if egg_info and os.path.exists(theme_vars_fp):
            config = SafeConfigParser()
            config.read(theme_vars_fp)
            
            for section in config.sections():
                for option in config.options(section):
                    key = section + '_' + option
                    val = config.get(section, option)
                    if section == 'multiple_templates':
                        val = val.split(',')
                    res[key] = val

        return res

    def add_template_vars(self, output_dir, vars):

        egg_info = pluginlib.find_egg_info_dir(output_dir)
        theme_vars_fp = os.path.join(egg_info, 'theme_vars.txt')

        if egg_info and os.path.exists(theme_vars_fp):
            config = SafeConfigParser()
            config.read(theme_vars_fp)

            # Update qplone3_theme used_subtemplate option
            sec, opt = 'qplone3_theme', 'used_subtemplates'
            val = filter(None,[st.strip() \
                         for st in config.get(sec,opt).split(',')])
            val.append(self.name)
            config.set(sec, opt, ','.join(set(val)))

            # Add subtemplate vars
            if self.shared_vars:
                thesection = self.name
                if config.has_section(thesection):
                    msection = 'multiple_templates'
                    moption = self.name

                    if not config.has_section(msection):
                        config.add_section(msection)

                    val = []
                    if config.has_option(msection, moption):
                        val = config.get(msection, moption).split(',')
                    else:
                        val.append(moption)
                    thesection = "%s_%d"%(moption,len(val))
                    val.append(thesection)

                    config.set(msection, moption, ','.join(val))

                config.add_section(thesection)
                for k in self.shared_vars:
                    config.set(thesection, k, vars[k])

            # Save theme_vars.txt file
            theme_file = file(theme_vars_fp,'w')
            config.write(theme_file)
            theme_file.close()
