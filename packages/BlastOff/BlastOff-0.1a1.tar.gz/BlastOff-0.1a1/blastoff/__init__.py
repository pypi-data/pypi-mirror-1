
from paste.deploy.converters import asbool
from paste.script.templates import BasicPackage, var

class BlastOffPackage(BasicPackage):
    _template_dir = 'template'
    summary = "A Pylons template providing a working site skeleton configured with SQLAlchemy, mako, repoze.who, schemabot and ToscaWidgets."
    egg_plugins = ['PasteScript', 'Pylons']
    vars = [
        var(
            'sqlalchemy_url',
            'The SQLAlchemy URL to the database to use',
            default='sqlite:///%(here)s/development.db'
        ),
        var(
            'email_confirmation',
            'True/False: New users must click activation link from confirmation email',
            default=True
        ),
        var(
            'default_user',
            'Default username to create, password will match username (leave blank for no default user)',
            default=''
        ),
    ]
    
    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        vars['email_confirmation'] = asbool(vars.get('email_confirmation', 'false'))
    

