import string
import os

class StringTemplatePlugin(object):
    extension = "tmpl"

    def __init__(self, extra_vars_func=None, config=None):
        self.get_extra_vars = extra_vars_func
        if config:
            self.config = config
        else:
            self.config = dict()

    def _load_template(self, template_name):
        parts = template_name.split('.')
        template_filename = "%s.%s" % (parts.pop(), self.extension)
        template_path = os.path.join(*parts)
        template_file_path = os.path.join(template_path, template_filename)
        template_file = open(template_file_path)
        template_obj = string.Template(template_file.read())
        template_file.close()
        return template_obj

    def render(self, info, format="html", fragment=False, template=None):
        vars = info
        if callable(self.get_extra_vars):
            vars.update(self.get_extra_vars())
        template_obj = self._load_template(template)
        return template_obj.safe_substitute(**vars)
    