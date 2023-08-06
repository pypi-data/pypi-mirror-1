import os
import cgi
import pkg_resources
import logging
from docutils import core
from repoze import trac
from clue.app import project
from clue.app import utils
from clue.themer import theme
from cluebin import pastebin
from cluebin import sqldata

logger = logging.getLogger('cluemapper')


def name_sort(prj1, prj2):
    """Sort by name attribute on the projects.

      >>> class Mock(object):
      ...     def __init__(self, **kw): self.__dict__.update(kw)

      >>> name_sort(Mock(name='foo'), Mock(name='bar'))
      1

    """

    res = cmp(prj1.name, prj2.name)
    if res == 0:
        return cmp(prj1.prjid, prj2.prjid)
    return res


class ControllerException(Exception):
    pass


class NoSuchProjectError(ControllerException):

    def __init__(self, prjid, msg=None):
        self.prjid = prjid
        msg = msg or 'No such project: ' + prjid
        super(NoSuchProjectError, self).__init__(msg)


class ControllerApp(object):
    """Middleware for accessing multiple trac projects.

      >>> from clue.tools.testing import Mock, MockDict
      >>> from clue.app import config
      >>> m = Mock(render=lambda: '')
      >>> loader = Mock(load=lambda x: Mock(generate=lambda **kw: m))
      >>> app = ControllerApp({'cluemapper.config': MockDict(projects=[],
      ...                                                    managers=[],
      ...                                                    base={}),
      ...                      'cluemapper.workingdir': '',
      ...                      'cluemapper.templateloader': loader})
      >>> app({'wsgi.url_scheme': 'http',
      ...      'SERVER_NAME': 'somehost.com',
      ...      'SERVER_PORT': '80'}, lambda x, y: None)
      ''

      ''

      """

    def __init__(self, global_config):
        self.global_config = global_config
        self.apps = {}
        self.projectapps = {}
        self._pastebin_app = None

    def __call__(self, environ, start_response):
        try:
            return self._call(environ, start_response)
        except NoSuchProjectError, err:
            kwargs = {'error_message': str(err),
                      'error_extended': None}
            start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
            loader = self.global_config['cluemapper.templateloader']
            return loader.load('error-404.html').generate(**kwargs).render()

    def _call(self, environ, start_response):
        path = environ.get('PATH_INFO', None)
        if not path or path == '/':
            pathname = 'index'
        elif path.startswith('/p/'):
            return self.access_project(environ, start_response)
        else:
            pieces = path.split('/')
            pathname = pieces[1]

        appname = 'page_'+pathname
        return getattr(self, appname)(environ, start_response)

    def access_project(self, environ, start_response):
        parts = environ['PATH_INFO'].split('/')
        script = environ['SCRIPT_NAME']
        here = parts[1]
        prjid = parts[2]

        cluemapperconfig = self.global_config['cluemapper.config']
        if not 'project:'+prjid in cluemapperconfig.keys():
            raise NoSuchProjectError(prjid)

        app = self.projectapps.get(prjid)
        prjconfig = cluemapperconfig['project:'+prjid]

        if app is None:
            app = trac.make_trac({}, env_path=prjconfig['tracenv'])
            self.projectapps[prjid] = app
            logger.debug('controller: registered new project app %r'
                         % prjid)

        newenv = dict(environ)
        newenv['SCRIPT_NAME'] = '%s/%s/%s' % (script, here, prjid)
        newenv['PATH_INFO'] = '/%s' % '/'.join(parts[3:])
        return app(newenv, start_response)

    def page_paste(self, environ, start_response):
        if self._pastebin_app is None:
            pb = utils.PathBuilder(self.global_config['cluemapper.workingdir'])
            shared_db = pb(os.path.join('etc', 'cluemapper', 'cluemapper.db'))
            datastore = sqldata.SqlPasteDataStore('sqlite:///'+shared_db)
            datastore.setup_tables()

            app = self._pastebin_app = pastebin.make_app(self.global_config,
                                                         datastore)
            app.display_tag_line = False

        newenv = dict(environ)
        pi = [x.strip() for x in environ['PATH_INFO'].split('/') if x.strip()]
        if pi:
            newenv['SCRIPT_NAME'] = environ['SCRIPT_NAME'] + '/' + pi[0]

        if len(pi) > 1:
            newenv['PATH_INFO'] = '/' + '/'.join(pi[1:])
        else:
            newenv['PATH_INFO'] = ''

        return self._pastebin_app(newenv, start_response)

    def page_createproject(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])

        cluemapperconfig = self.global_config['cluemapper.config']
        workingdir = self.global_config['cluemapper.workingdir']
        loader = self.global_config['cluemapper.templateloader']

        pmanager = project.ProjectManager(environ, self.global_config)
        if not pmanager._can_manage():
            return loader.load('access-denied.html').generate().render()

        data = environ['wsgi.input'].read()
        if data:
            formargs = cgi.parse_qs(data)
            name = formargs['name'][0]
            themesel = formargs['theme'][0]

            prj = pmanager.create_project(name, themesel)
            tmpl = loader.load('project-created.html')
            prjurl = '/pm/p/' + prj.prjid
            return tmpl.generate(prjid=prj.prjid,
                                 name=name, prjurl=prjurl).render()

    def page_index(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        items = ''
        cluemapperconfig = self.global_config['cluemapper.config']
        pmanager = project.ProjectManager(environ, self.global_config)
        wd = self.global_config['cluemapper.workingdir']

        tmanager = theme.ThemeManager(wd, cluemapperconfig)
        loader = self.global_config['cluemapper.templateloader']
        prjs = sorted(pmanager.projects, name_sort)

        username = environ.get('REMOTE_USER', '')
        logout = ''
        if username != 'anonymous':
            logout = '<a href="/logout">Log Out</a>'

        version = pkg_resources.get_distribution('ClueMapper').version
        kwargs = {'projects': prjs,
                  'username': username,
                  'can_manage_projects': pmanager._can_manage(),
                  'themes': tmanager.themes,
                  'base_url': environ.get('SCRIPT_NAME', '/pm'),
                  'version': version}
        return loader.load('main.html').generate(**kwargs).render()

    def page_readme(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        readme = self.global_config['cluemapper.metadata']['Description']

        return '<html><head><title>README</title></head>' \
               '<body><div id="main"><pre>%s</pre></div></body></html>' \
               % readme


def make_app(global_config, **kw):
    """Factory for creating new controller apps.

      >>> make_app({'cluemapper.config': None, 'cluemapper.workingdir': None,
      ...           'cluemapper.templateloader': None})
      <clue.app.controller.ControllerApp ...>
    """

    return ControllerApp(global_config)
