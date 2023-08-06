"""
Local templates for the qplone3_theme
"""
import os, sys, re, datetime
from ConfigParser import SafeConfigParser
from paste.script import pluginlib

from zopeskel.base import var
from zopeskel.localcommands import ZopeSkelLocalTemplate
from quintagroup.themetemplate.localcommands import QThemeSubTemplate

RESP = re.compile("\s+")
REBAN = re.compile("[\\\/\,\.\+\-\*\%\~\@\#\$\^\&\|\;\:\?\(\)\=\[\]\{\}\_]+")


class SkinLayerSubTemplate(QThemeSubTemplate):
    """
    A Plone Skin layer skeleton
    """
    _template_dir = 'templates/skinlayer'
    summary = "A Plone 3 Skin Layer"

    compo_template_markers = [
        ('layer4Skin',   'extra layer stuff goes here'),
    ]

    vars = [
      var('layer_name', 'Skin Layer name (should not contain spaces)',
           default="skin_layer"),
      var('insert_type', 'Where insert the layer ("after" or "before")', default="after"),
      var('insert_control_layer',
          'Layer after or before which your layer will be inserted, "*" accepted, which mean all',
          default='custom'),
           ]


class CSSSubTemplate(QThemeSubTemplate):
    """
    A Plone CSS resource skeleton
    """
    _template_dir = 'templates/cssresource'
    summary = "A Plone 3 CSS resource template"
    

    vars = [
      var('css_resource_name', 'Name of CSS resource',
           default="main.css"),
      var('css_file_path', 'Path to CSS file. If no path-empty file will be created.',
           default=''),
      var('cssreg_media', 'Optional.Possible values:screen,print,projection,handheld',
           default="screen", ),
      var('cssreg_rel', 'Optional', default="stylesheet"),
      var('cssreg_rendering', 'Optional.Possible values:import,link,inline', default="inline"),
      var('cssreg_cacheable', '', default="True"),
      var('cssreg_compression', 'Compression type', default="safe"),
      var('cssreg_cookable', 'Boolean, aka merging allowed', default="True"),
      var('cssreg_enables', 'Optional.Boolean', default="1"),
      var('cssreg_expression', 'Optional.A tal condition.', default=""),
           ]

    def pre(self, command, output_dir, vars):
        """ Set 'css_resource_content' value from css_file_path
        """
        super(CSSSubTemplate, self).pre(command, output_dir, vars)

        vars['css_resource_content'] = ''
        if os.path.isfile(vars['css_file_path']):
            vars['css_resource_content'] = file(vars['css_file_path'],'rb').read()


class JSSubTemplate(QThemeSubTemplate):
    """
    A Plone JS resource skeleton
    """
    _template_dir = 'templates/jsresource'
    summary = "A Plone 3 JS resource template"
    

    vars = [
      var('js_resource_name', 'Name of JS resource', default="foo.js"),
      var('js_file_path', 'Path to JS file. If no path - empty file will be created',
          default=''),
      var('jsreg_inline', 'Optional.Boolean', default="False"),
      var('jsreg_cacheable', '', default="True"),
      var('jsreg_compression', 'Compression type.Possible:none,safe,full,safe-encode,full-encode',
          default="safe"),
      var('jsreg_cookable', 'Boolean, aka merging allowed', default="True"),
      var('jsreg_enables', 'Optional.Boolean', default="1"),
      var('jsreg_expression', 'Optional.A tal condition.', default=""),
           ]

    def pre(self, command, output_dir, vars):
        """ Set 'js_resource_content' value from js_file_path
        """
        super(JSSubTemplate, self).pre(command, output_dir, vars)
        
        vars['js_resource_content'] = ''
        if os.path.isfile(vars['js_file_path']):
            vars['js_resource_content'] = file(vars['js_file_path'],'rb').read()


class ViewletOrderSubTemplate(QThemeSubTemplate):
    """
    A Plone Order Viewlet skeleton
    """
    _template_dir = 'templates/viewlet'
    summary = "A Plone 3 Order Viewlet template"
    
    # list of 2 item tuple -
    # (compotemplate_name, compo marker), for ex.:
    compo_template_markers = []

    shared_vars = ['viewlet_profile_marker',]

    vars = [
      var('viewlet_name', "Viewlet name", default='example'),
      var('viewlet_manager_interface', "Viewlet manager interface",
          default="plone.app.layout.viewlets.interfaces.IPortalHeader"),
      var('viewlet_manager_name', "Viewlet manager name", default='plone.portalheader'),
      var('viewlet_permission', "Viewlet permission", default="zope2.View"),


      var('insert_type', 'Where insert the viewlet ("after" or "before")', default="after"),
      var('insert_control_viewlet', 'Viewlet after or before which your viewlet will be inserted, ' \
          '"*" accepted, which mean all', default='*'),

      var('layer_interface', "Layer interface for registry this viewlet on", 
          default=".interfaces.IThemeSpecific"),
      var('layer_name', "Layer name for registry this viewlet on", default=""),
      #var('skinname', "Skin name, for bind viewlet to, '*' - mean for all", default=""),
      #var('skinbase', "Base skin, for get viewlets from", default=""),
           ]

    def pre(self, command, output_dir, vars):
        """ Set 'css_resource_content' value from css_file_path
        """
        super(ViewletOrderSubTemplate, self).pre(command, output_dir, vars)

        vn_lower_nospc = RESP.sub('',vars['viewlet_name']).lower()
        vn_lower_under = RESP.sub('_',vars['viewlet_name']).lower()
        VnCamel = ''.join([i.capitalize() for i in REBAN.sub(' ',vars['viewlet_name']).split()])
        vars['viewlet_class_name'] = VnCamel
        vars['viewlet_interface_name'] = "I"+VnCamel
        vars['viewlet_template_name'] = vn_lower_nospc+'_viewlet.pt'

        viewlet_profile_marker = "[order_%s] viewlet stuff goes here" % \
            '.'.join([vars['viewlet_manager_name'], vars['qplone3_theme_skinname'], 
                      vars['qplone3_theme_skinbase']])
        
        vars['add_order_tag'] = self.add_order_tag(output_dir, vars, viewlet_profile_marker)
        vars['viewlet_profile_marker'] = viewlet_profile_marker
        self.compo_template_markers.append(
            ('viewlet_profiles',viewlet_profile_marker))


    def add_order_tag(self, output_dir, vars, pmarker):
        need_update = True
        egg_info = pluginlib.find_egg_info_dir(output_dir)
        theme_vars_fp = os.path.join(egg_info, 'theme_vars.txt')

        if egg_info and os.path.exists(theme_vars_fp):
            config = SafeConfigParser()
            config.read(theme_vars_fp)

            sec, opt = 'qplone3_theme', 'used_subtemplates'
            used_subtemplates = filter(None,[st.strip() \
                         for st in config.get(sec,opt).split(',')])
            
            if self.name in used_subtemplates:
                sections = [self.name,]
                if config.has_section('multiple_templates') and \
                  config.has_option('multiple_templates',self.name):
                    ms_sections = config.get('multiple_templates',self.name)
                    sections = [s.strip() for s in ms_sections.split(',')]

                pmarkers = [config.get(sec, 'viewlet_profile_marker') \
                            for sec in sections]
                if pmarker in pmarkers:
                    need_update = False

        return need_update


class ViewletHiddenSubTemplate(QThemeSubTemplate):
    """
    A Plone Hidden Viewlet skeleton
    """
    _template_dir = 'templates/viewlet_hidden'
    summary = "A Plone 3 Hidden Viewlet template"

    shared_vars = ['viewlet_profile_marker',]

    compo_template_markers = []
    
    vars = [
      var('viewlet_name', "Viewlet name", default='plone.global_sections'),
      var('viewlet_manager_name', "Viewlet manager name", default='plone.portalheader'),
      #var('skinname', "Skin name, for bind viewlet to, may be '*'", default=""),
           ]

    def pre(self, command, output_dir, vars):
        """ Set 'css_resource_content' value from css_file_path
        """
        super(ViewletHiddenSubTemplate, self).pre(command, output_dir, vars)
         
        viewlet_profile_marker = "[hidden_%s] viewlet stuff goes here" % \
            '.'.join([vars['viewlet_manager_name'], vars['qplone3_theme_skinname']])

        vars['add_hidden_tag'] = self.add_hidden_tag(output_dir, vars, viewlet_profile_marker)
        vars['viewlet_profile_marker'] = viewlet_profile_marker
        self.compo_template_markers.append(
            ('viewlet_hidden_profiles',viewlet_profile_marker))


    def add_hidden_tag(self, output_dir, vars, pmarker):
        add_hidden = True
        egg_info = pluginlib.find_egg_info_dir(output_dir)
        theme_vars_fp = os.path.join(egg_info, 'theme_vars.txt')

        if egg_info and os.path.exists(theme_vars_fp):
            config = SafeConfigParser()
            config.read(theme_vars_fp)

            sec, opt = 'qplone3_theme', 'used_subtemplates'
            used_subtemplates = filter(None,[st.strip() \
                         for st in config.get(sec,opt).split(',')])
            
            if self.name in used_subtemplates:
                sections = [self.name,]
                if config.has_section('multiple_templates') and \
                  config.has_option('multiple_templates',self.name):
                    ms_sections = config.get('multiple_templates',self.name)
                    sections = [s.strip() for s in ms_sections.split(',')]

                pmarkers = [config.get(sec, 'viewlet_profile_marker') \
                            for sec in sections]
                if pmarker in pmarkers:
                    add_hidden = False
        return add_hidden

class ImportSubTemplate(QThemeSubTemplate):
    """
    A skeleton for importing zexp objects into portal on theme installation
    """
    _template_dir = 'templates/importing'
    summary = "A template for importing zexp-objects into portal on installation"
    
    def pre(self, command, output_dir, vars):
        """ Set timestamp var for generate import_steps profile id
        """
        super(ImportSubTemplate, self).pre(command, output_dir, vars)

        vars['timestamp'] = datetime.date.today().strftime("%Y%m%d")
        vars['already_used'] = self.already_used(vars)

    def already_used(self, vars):
        used = vars.get('qplone3_theme_used_subtemplates','').split(',')
        return self.name in filter(None,[st.strip() for st in used])
