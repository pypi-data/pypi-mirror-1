#-*- coding: utf-8 -*-
from paste.script.templates import Template, var
from tempita import paste_script_template_renderer, Template as Templ
from paste.deploy.converters import asbool

class Create(Template):
    _template_dir = ('pylons_gae', 'default_project')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = 'Pylons appengine application template'
    egg_plugins = ['PasteScript', 'Pylons']
    vars = []
    ensure_names = ['description', 'author', 'author_email', 'url']
    
    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        vars['template_engine'] = "mako"
        vars['babel_templates_extractor'] = \
                ("('templates/**.mako', 'mako', {'input_encoding': 'utf-8'})"
                 ",\n%s#%s" % (' ' * 4, ' ' * 8))
                
        for name in self.ensure_names:
            vars.setdefault(name, '')

        vars['version'] = vars.get('version', '0.1')
        vars['zip_safe'] = asbool(vars.get('zip_safe', 'false'))
        vars['sqlalchemy'] = asbool(vars.get('sqlalchemy', 'false'))
#        
#        tmpl = Templ.from_filename("config.py", namespace={}, encoding=None)
#        tmpl.substitute(package=package_logger)
#        
#        
        
#        #supprimer le répertoire actuel du projet
#        from distutils import dir_util
#        dir_util.remove_tree("/home/fedtech/cassandra")


