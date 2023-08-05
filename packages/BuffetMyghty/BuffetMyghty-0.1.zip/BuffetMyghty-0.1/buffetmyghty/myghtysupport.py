import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from myghty.interp import Interpreter

class MyghtyTemplatePlugin(object):
    extension = "myt"

    def __init__(self, extra_vars_func=None, config=None):
        self.get_extra_vars = extra_vars_func
        if config:
            self.config = config
        else:
            self.config = dict()

    def _get_path_and_filename(self, dotted_tmpl_path):
        parts = dotted_tmpl_path.split('.')
        template_file_path = os.path.join(*parts)
        template_path, template_filename = os.path.split(template_file_path)
        template_filename = "%s.%s" % (template_filename, self.extension)
        return template_path, template_filename

    def _load_template(self, template_path):
        template_path, template_filename = self._get_path_and_filename(template_path)
        if callable(self.get_extra_vars):
            extra_vars = self.get_extra_vars()
        else:
            extra_vars = dict()
        cache_location = self.config.get('myghty.data_dir', None)
        interpreter = Interpreter(component_root = template_path,
                                  allow_globals=extra_vars.keys(),
                                  global_args=extra_vars,
                                  data_dir=cache_location)
        return interpreter

    def render(self, info, format="html", fragment=False, template=None):
        vars = info
        tmpl_interpreter = self._load_template(template)
        junk, template_filename = self._get_path_and_filename(template)
        buf = StringIO()
        tmpl_interpreter.execute(template_filename, request_args=vars, out_buffer=buf)
        return buf.getvalue()
