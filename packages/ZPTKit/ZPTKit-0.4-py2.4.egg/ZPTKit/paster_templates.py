import os
from paste.script.templates import Template

class ZPT(Template):

    _template_dir = 'paster_templates/zpt'
    summary = "A Zope Page Template project"

    def post(self, command, output_dir, vars):
        setup = os.path.join(output_dir, 'setup.py')
        command.insert_into_file(
            setup, 'package_data',
            "%r: ['templates/*.pt', 'templates/admin/*.pt'],\n" % vars['package'],
            indent=True)
