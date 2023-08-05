from paste.script.appinstall import Installer
from paste.script.templates import Template

class ZContactTemplate(Template):
    _template_dir = 'install_template'
    summary = 'ZContact application template'

class ZContactInstaller(Installer):
    default_config_filename = 'zcontact'

    def write_config(self, command, filename, vars):
        ZContactTemplate('zcontact').run(command, filename, vars)
