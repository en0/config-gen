from jinja2 import Template


class TemplateProcessor(object):

    def __init__(self, fp):
        self._dest = fp.readline().strip()
        self._template = Template(fp.read().decode('utf-8'))

    @property
    def target_path(self):
        return self._dest

    def render_file(self, profile, ks, path=None):
        _path = path or self.target_path
        with open(_path, 'w') as _fp:
            self.render_fp(profile, ks, _fp)

    def render_fp(self, profile, ks, fp):
        fp.write(self.render(profile, ks))

    def render(self, profile, ks):
        _dict = ks.get_profile_dict(profile)
        return self._template.render(_dict)
