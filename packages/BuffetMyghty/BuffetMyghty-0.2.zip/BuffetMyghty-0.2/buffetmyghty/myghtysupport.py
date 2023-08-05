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
        if callable(self.get_extra_vars):
            extra_vars = self.get_extra_vars()
        else:
            extra_vars = dict()
        template_root = config.get('myghty.component_root', '.')
        cache_location = self.config.get('myghty.data_dir', None)
        self.interpreter = Interpreter(component_root = template_root,
                                  allow_globals=extra_vars.keys(),
                                  global_args=extra_vars,
                                  data_dir=cache_location)

    def _get_template_path(self, dotted_tmpl_path):
        parts = dotted_tmpl_path.split('.')
        template_file_path = os.path.join(*parts)
        return template_file_path
##        template_path, template_filename = os.path.split(template_file_path)
##        template_filename = "%s.%s" % (template_filename, self.extension)
##        return template_path, template_filename

    def load_template(self, template_path):
        pass
##        template_path, template_filename = self._get_path_and_filename(template_path)
##        if callable(self.get_extra_vars):
##            extra_vars = self.get_extra_vars()
##        else:
##            extra_vars = dict()
##        cache_location = self.config.get('myghty.data_dir', None)
##        interpreter = Interpreter(component_root = template_path,
##                                  allow_globals=extra_vars.keys(),
##                                  global_args=extra_vars,
##                                  data_dir=cache_location)
##        return interpreter

    def render(self, info, format="html", fragment=False, template=None):
        vars = info
        template_path = "%s.%s" % (self._get_template_path(template), self.extension)
        buf = StringIO()
        self.interpreter.execute(template_path, request_args=vars, out_buffer=buf)
        return buf.getvalue()
