import webob


class RedirectApp(object):
    '''Simple middleware for configurable redirects.
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
        request = webob.Request(environ)
        response = webob.Response(content_type='text/plain')

        newurl = self.main_redirect
        if self.relative_redirect:
            part1 = request.application_url
            if part1.endswith('/'):
                part1 = part1[:-1]
            part2 = self.main_redirect
            if part2.startswith('/'):
                part2 = part2[1:]
            newurl = part1 + '/' + part2
        response.headers['Location'] = newurl
        response.status = '301 Moved Permanently'

        return response(environ, start_response)


def make_app(global_config, main_redirect, relative_redirect=None):
    '''Factory for redirect app.

      >>> make_app(None, main_redirect='somewhere')
      <clue.app.redirect.RedirectApp ...>
    '''

    return RedirectApp(main_redirect, relative_redirect)
