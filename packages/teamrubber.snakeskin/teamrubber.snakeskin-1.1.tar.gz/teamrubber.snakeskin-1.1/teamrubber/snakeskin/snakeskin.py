import copy
import datetime

from zopeskel import BasicNamespace
from zopeskel.base import get_var
from paste.script import templates

var=templates.var

class SnakeSkin(BasicNamespace):
    _template_dir = 'templates/snakeskin'
    summary = "A Theme for Plone 3.1 based on another theme egg."
    required_templates = ['basic_namespace']
    use_cheetah = True
    egg_plugins = ["teamrubber.snakeskin", ]

    vars = copy.deepcopy(BasicNamespace.vars)
    get_var(vars, 'namespace_package').default = 'clienttheme'
    get_var(vars, 'namespace_package').description = 'Namespace package (like clienttheme)'
    get_var(vars, 'description').default = 'A theme based on an existing arbitrary plone 3 theme.'
    get_var(vars, 'zip_safe').default = False
    
    vars = vars[:3] + [
        var("theme_name", "The name of this theme", default="Client Skin"),
        var("base_theme", "The package containing the theme to base on (the name of the egg)", default="plonetheme.example"),
        var("basename", "The name of the Zope skin layer the above theme provides", default="My Theme"),
    ] + vars[3:]

    def pre(self, command, output_dir, vars):
        vars['timestamp'] = datetime.date.today().strftime("%Y%m%d")
        super(SnakeSkin, self).pre(command, output_dir, vars)


