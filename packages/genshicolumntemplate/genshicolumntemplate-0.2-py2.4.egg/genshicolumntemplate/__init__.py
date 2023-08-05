from paste.script import templates
import pkg_resources

class GenshiColumnTemplate(templates.Template):

    egg_plugins = ['GenshiColumnTemplate']
    required_templates = ['tggenshi']
    _template_dir = pkg_resources.resource_filename("genshicolumntemplate",
                                                    "template")
    use_cheetah = True
    summary = "Adds a 3 column layout to the standard genshi quickstart."

#     def post(self, command, output_dir, vars):
#         templates.Template.post(self, command, output_dir, vars)
#         try:
#             path = os.path.join(output_dir,
#                      vars['package'] + '/controllers.py')
#             os.remove(path)
#             print 'Removing', path
#         except OSError:
#             pass
