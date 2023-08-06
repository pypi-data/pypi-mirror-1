from os.path import join

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader


class Jinja2Template(object):
    default_template = 'default.html'

    def __init__(self, settings):
        self.settings = settings
        self.env = Environment(loader=ChoiceLoader([
            FileSystemLoader(join(self.settings['project_dir'],
                                  'templates')),
            PackageLoader('lanyon')]))
        self.env.filters['datetimeformat'] = self.datetimeformat

    def datetimeformat(self, value, format='%H:%M / %d-%m-%Y'):
        return value.strftime(format)

    def render(self, context):
        template_name = context['article']['headers']['template']
        if template_name == 'self':
            template = self.env.from_string(context['article']['body'])
        else:
            template = self.env.get_template(template_name)
        output = template.render(context['article']['headers'],
                                 body=context['article']['body'],
                                 articles=context['articles'],
                                 RELPATH_ROOT=context['RELPATH_ROOT'],
                                 BUILD_TIME=context['BUILD_TIME'])
        return output

