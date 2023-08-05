import os
from glob import glob

from turbogears.command.quickstart import TGTemplate
import pkg_resources

class GenshiTemplate(TGTemplate):

    required_templates = ["turbogears"]
    _template_dir = pkg_resources.resource_filename(
                            "gsquickstart.templates", 
                            "quickstart")
    summary = "web framework with genshi"
    use_cheetah = True

    def post(self, command, output_dir, vars):
        TGTemplate.post(self, command, output_dir, vars)
        for file in ['login.kid', 'master.kid', 'welcome.kid']:
            path = os.path.join(output_dir, vars['package'], 'templates', file)
            question = "Delete Kid template '%s'" % command.shorten(path)
            if os.path.exists(path) and command.command_name != 'update' or \
              command.ask(question, default=False):
                try:
                    os.remove(path)
                    print 'Removing', path
                except OSError:
                    pass
