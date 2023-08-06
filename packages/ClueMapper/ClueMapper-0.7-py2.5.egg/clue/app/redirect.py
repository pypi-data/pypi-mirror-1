

class RedirectApp(object):
    '''Simple middleware for configurable redirects.

      >>> app = RedirectApp(None, '/foo/')
      >>> app.gen_url({'PATH_INFO': ''})
      '/foo'
      >>> app.gen_url({'PATH_INFO': '/bar'})
      '/foo/bar'
      >>> ignored = app({'PATH_INFO': ''}, lambda x, y: None)

    '''

    def __init__(self, main_redirect, relative_redirect=None):
        self.main_redirect = main_redirect
        self.relative_redirect = relative_redirect

    def gen_url(self, environ):
        loc = self.main_redirect
        if environ['PATH_INFO'] != '/' and self.relative_redirect:
            loc = self.relative_redirect
            if loc.endswith('/'):
                loc = loc[:-1]
            loc += environ['PATH_INFO']
        return loc

    def __call__(self, environ, start_response):
        loc = self.gen_url(environ)
        start_response('301 Moved Permanently', [('Location', loc)])
        return ''


def make_app(global_config, main_redirect, relative_redirect=None):
    '''Factory for redirect app.

      >>> make_app(None, main_redirect='somewhere')
      <clue.app.redirect.RedirectApp ...>
    '''

    return RedirectApp(main_redirect, relative_redirect)
