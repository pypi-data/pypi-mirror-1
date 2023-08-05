from paste.script import templates
import pkg_resources

class Registration(templates.Template):

    egg_plugins = ['Registration']
    _template_dir = pkg_resources.resource_filename("registration", "template")
    summary = "Provides a template for simple user registraton and verification."
    required_templates = ['turbogears']
    use_cheetah = True
