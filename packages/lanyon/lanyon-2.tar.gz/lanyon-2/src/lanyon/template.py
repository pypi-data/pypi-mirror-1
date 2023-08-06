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

    def render_string(self, template_str, **kwargs):
        """Use `template_str` as a template"""
        template = self.env.from_string(template_str)
        return template.render(**kwargs)

    def render(self, template_name, **kwargs):
        """Use `template_name` as a template"""
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

