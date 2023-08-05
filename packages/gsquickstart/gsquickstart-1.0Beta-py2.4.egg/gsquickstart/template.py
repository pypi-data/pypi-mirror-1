from turbogears.command.quickstart import TGTemplate
import pkg_resources

class GenshiTemplate(TGTemplate):

    required_templates = ["tgbase"]
    _template_dir = pkg_resources.resource_filename(
                            "gsquickstart.templates", 
                            "quickstart")
    summary = "web framework with genshi"
    use_cheetah = True
