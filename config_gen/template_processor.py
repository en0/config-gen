from jinja2 import Template


class TemplateProcessor(object):

    def __init__(self, fp):
        self._dest = fp.readline().strip()
        self._template = Template(fp.read().decode('utf-8'))

    @property
    def target_path(self):
        return self._dest

    def render_file(self, ks, path=None):
        _path = path or self.target_path
        with open(_path, 'w') as _fp:
            self.render_fp(ks, _fp)

    def render_fp(self, ks, fp):
        fp.write(self.render(ks))

    def render(self, ks):
        return self._template.render(**ks)
