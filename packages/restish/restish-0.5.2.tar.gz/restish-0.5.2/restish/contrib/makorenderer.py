"""
Mako templating renderer than uses Mako's template lookup to find the template
to render.

An instance of a MakoRenderer can be used as the restish.templating.renderer in
the WSGI environ.

Recommended setup:

  * load templates from a directory of data files inside the application package
  * the disk templates and generated content are UTF-8 encoded
  * variable substitutions are converted to unicode instances and automatically
    HTML escaped.

e.g.

    environ['restish.templating.renderer'] = MakoRenderer(
        directories=[pkg_resources.resource_filename('yourpackage', 'templates')],
        module_directory=os.path.join(cache_dir, 'templates'),
        input_encoding='utf-8', output_encoding='utf-8',
        default_filters=['unicode', 'h'])
"""

from mako.lookup import TemplateLookup


class MakoRenderer(object):

    def __init__(self, *a, **k):
        self.lookup = TemplateLookup(*a, **k)

    def __call__(self, template, args={}):
        return self.lookup.get_template(template).render(**args)

