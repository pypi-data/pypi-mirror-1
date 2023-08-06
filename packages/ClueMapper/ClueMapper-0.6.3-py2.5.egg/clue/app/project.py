import string
import os
from trac import env
from trac import perm
import tempfile
import logging
import subprocess
import clue.app
from clue.app import config
from clue.app import utils
logger = logging.getLogger('cluemapper')


class ProjectError(Exception):

    def __init__(self, m, extended=None):
        Exception.__init__(self, m)
        self.extended = extended


class PermissionError(Exception):
    pass


class Project(object):
    prjid = None
    tracpath = None
    url = None
    name = None
    description = None
    themeid = None

    def __init__(self, prjid):
        self.prjid = prjid


class ProjectManager(object):
    """A utility for dealing with projects."""

    def __init__(self, environ, global_conf={}):
        self._environ = environ
        self._global_conf = global_conf
        self._projects = None
        self._cached_system_trac = None
        self._tracenvs = {}

    @property
    def _cluemapperconfig(self):
        return self._environ.get('cluemapper.config',
                                 self._global_conf.get('cluemapper.config',
                                                       None))

    @property
    def _workingdir(self):
        return self._environ.get('cluemapper.workingdir',
                                 self._global_conf.get('cluemapper.workingdir',
                                                       None))

    @property
    def _username(self):
        return self._environ.get('REMOTE_USER', 'anonymous')

    @property
    def projects(self):
        if self._projects is not None:
            return self._projects.values()

        self._allprojects = {}
        self._projects = {}
        for prjid, prjconfig in self._cluemapperconfig.projects:
            prj = self._project_factory(prjid, prjconfig)
            if self._can_access(prj):
                self._projects[prj.prjid] = prj
            self._allprojects[prj.prjid] = prj
        return self._projects.values()

    def get_project(self, prjid):
        self.projects # to make sure cached value is populated
        if prjid in self._allprojects and prjid not in self._projects:
            raise utils.AccessError('No access to project with id %r' % prjid)
        return self._projects[prjid]

    def get_project_theme(self, prjid):
        self.projects # to make sure cached value is populated
        # no access check for this one
        return self._allprojects[prjid].themeid

    def update_project(self, prjid, fields):
        prj = self.get_project(prjid)
        projectconfig = self._cluemapperconfig['project:'+prjid]
        for k, v in fields.items():
            projectconfig[k] = v
        self._cluemapperconfig.save()

        self._projects = None

    def _gen_unique_id(self, name):
        normalized = ''
        acceptable = string.ascii_letters + string.digits + '_-'
        for x in name:
            if x in acceptable:
                normalized += x.lower()
            elif normalized[-1] != '-':
                normalized += '-'
        newname = normalized
        for x in range(1, 20):
            if 'project:'+newname not in self._cluemapperconfig.keys():
                break
            newname = normalized + '-' + str(x)

        if 'project:'+newname in self._cluemapperconfig.keys():
            raise ProjectError('Could not generate new unique id for %r'
                               % name)

        return newname

    def _find_tracadminpath(self):
        """Figure out where trac-admin executable is located."""

        # are we in the parts directory of a buildout?
        cur = os.path.abspath(os.curdir)
        b = os.path.abspath(os.path.join(cur, '..', '..', 'bin', 'trac-admin'))
        if os.path.exists(b):
            self._cached_system_trac = b
            return b

        # or perhaps in a virtualenv root?
        b = os.path.join(cur, 'bin', 'trac-admin')
        if os.path.exists(b):
            self._cached_system_trac = b
            return b

        # none of the above is true? then lets search the system path
        for x in os.environ.get('PATH', '').split(os.path.pathsep):
            b = os.path.join(x, 'trac-admin')
            if os.path.exists(b):
                self._cached_system_trac = b
                return b

        # heh, no luck, lets just return no path
        return 'trac-admin'

    def _get_paths(self, prjid):
        base = self._cluemapperconfig['base']

        pb = utils.PathBuilder(self._workingdir)
        tracenvpath = pb(os.path.join(base['tracenv_base'], prjid))
        svnrepopath = pb(os.path.join(base['svnrepo_base'], prjid))
        tracadminpath = base.get('tracadminpath',
                                 pb(os.path.join(self._workingdir, 'bin',
                                                 'trac-admin')))

        if not os.path.exists(tracadminpath):
            tracadminpath = self._cached_system_trac or \
                            self._find_tracadminpath()
            self._cached_system_trac = tracadminpath

        return (tracadminpath, tracenvpath, svnrepopath)

    def create_project(self, prj_name, themeid=None):
        if not self._can_manage():
            raise PermissionError('Current user %r has not been assigned as a '
                                  'manager' % self._username)
        base = self._cluemapperconfig['base']
        prjid = self._gen_unique_id(prj_name)
        projectconfig = self._cluemapperconfig['project:'+prjid]

        if themeid:
            projectconfig['theme'] = themeid

        tracadminpath, tracenvpath, svnrepopath = self._get_paths(prjid)
        projectconfig['tracenv'] = tracenvpath
        projectconfig['svnrepo'] = svnrepopath
        pb = utils.PathBuilder(self._workingdir)
        for x in (svnrepopath, tracenvpath):
            parentdir = pb(os.path.dirname(x))
            if not os.path.exists(parentdir):
                os.makedirs(parentdir)

        logger.info('Creating new svn repo at: %r' % svnrepopath)
        self._execute(['svnadmin', 'create', svnrepopath])
        logger.info('Creating new trac env at: %r' % tracenvpath)
        cmd = [tracadminpath, tracenvpath, 'initenv',
               prj_name, 'sqlite:db/trac.db',
               'svn', svnrepopath]
        self._execute(cmd)
        logger.info('Setting up default permissions')
        self.reset_perms(prjid)
        logger.info('Setting up default trac properties')
        self.setup_default_trac(prjid)

        self._cluemapperconfig.save()
        logger.info('Project successfully created')

        prj = self._project_factory(prjid, projectconfig)
        return prj

    def _execute(self, cmd):
        handler, fname = tempfile.mkstemp()
        f = open(fname, 'w')
        try:
            try:
                ret = subprocess.call(cmd, stdout=f, stderr=f)
            except OSError, err:
                raise ProjectError('The cmd %r could not be executed, '
                                   'full cmd args are: %r'
                                   % (cmd[0], ' '.join(cmd)))
            if ret != 0:
                raise ProjectError('Error while executing %r' % ' '.join(cmd))
        finally:
            f.close()
            f = open(fname)
            self._lastlog = f.read()
            f.close()
            os.remove(fname)

        return ret

    def _open_tracenv(self, path):
        tracenv = self._tracenvs.get(path, None)
        if tracenv is not None:
            return tracenv
        tracenv = self._tracenvs[path] = env.open_environment(path, True)
        return tracenv

    def _project_factory(self, prjid, projectconfig):
        pb = utils.PathBuilder(self._workingdir)

        path = pb(projectconfig['tracenv'])
        tracenv = self._open_tracenv(path)

        p = Project(prjid)
        p.url = tracenv.project_url
        p.name = tracenv.project_name
        p.description = tracenv.project_description
        p.themeid = projectconfig.get('theme', None)
        p.tracpath = path

        return p

    def _can_manage(self):
        return self._username in self._cluemapperconfig.managers

    def _can_access(self, project):
        permsys = perm.PermissionSystem(self._open_tracenv(project.tracpath))
        return permsys.check_permission('WIKI_VIEW', self._username)

    DEFAULT_PERMS = {'anonymous': [],
                     'authenticated': [],
                     'member': [
                         'BROWSER_VIEW',
                         'CHANGESET_VIEW',
                         'FILE_VIEW',
                         'LOG_VIEW',
                         'MILESTONE_VIEW',
                         'REPORT_SQL_VIEW',
                         'REPORT_VIEW',
                         'ROADMAP_VIEW',
                         'SEARCH_VIEW',
                         'TICKET_VIEW',
                         'TIMELINE_VIEW',
                         'WIKI_VIEW',
                         'TICKET_CREATE',
                         'TICKET_MODIFY',
                         'WIKI_CREATE',
                         'WIKI_MODIFY',
                         ],
                     'manager': ['TRAC_ADMIN'],
                     }

    def reset_perms(self, prjid):
        tracadminpath, tracenvpath, svnrepopath = self._get_paths(prjid)

        for user, perms in self.DEFAULT_PERMS.items():
            ret = self._execute([tracadminpath, tracenvpath,
                                 'permission', 'remove', user, '*'])
            if ret != 0:
                raise ProjectError('Got error code %r when running permission'
                                   % ret)
            if len(perms) == 0:
                continue

            args = [tracadminpath, tracenvpath, 'permission', 'add', user]
            args.extend(perms)
            ret = self._execute(args)
            if ret != 0:
                raise ProjectError('Got error code %r when running permission'
                                   % ret)

        permmap = {}
        if 'base:permissions' in self._cluemapperconfig.keys():
            for user, v in self._cluemapperconfig['base:permissions'].items():
                permmap[user] = set([x.strip() for x in v.split(',')])
        for mgr in self._cluemapperconfig.managers:
            s = permmap.get(mgr, set())
            s.add('manager')
            permmap[mgr] = s

        for user, v in permmap.items():
            ret = self._execute([tracadminpath, tracenvpath,
                                 'permission', 'remove',
                                 user, '*'])
            if ret != 0:
                raise ProjectError('Got error code %r when running '
                                   'permission' % ret)

            args = [tracadminpath, tracenvpath, 'permission', 'add', user]
            args.extend(v)
            ret = self._execute(args)
            if ret != 0:
                raise ProjectError('Got error code %r when running '
                                   'permission: %r' % (ret, args))

        return 0

    def fix_paths(self, prjid):
        tracadminpath, tracenvpath, svnrepopath = self._get_paths(prjid)
        tracconffile = os.path.join(tracenvpath, 'conf', 'trac.ini')
        tracconfig = config.Config(tracconffile)
        clueconfig = self._cluemapperconfig
        pb = utils.PathBuilder(self._workingdir)
        tracconfig['account-manager']['password_file'] = \
            pb(clueconfig['base']['auth_file'])
        tracconfig['trac']['repository_dir'] = \
            pb(os.path.join(clueconfig['base']['svnrepo_base'], prjid))

        tracconfig['cluemapper']['database'] = 'sqlite:' + \
            pb(os.path.join('etc', 'cluemapper', 'cluemapper.db'))
        tracconfig.save()

    def get_trac_config(self, prjid):
        tracadminpath, tracenvpath, svnrepopath = self._get_paths(prjid)
        tracconffile = os.path.join(tracenvpath, 'conf', 'trac.ini')
        tracconfig = config.Config(tracconffile)
        return tracconfig

    def _setup_default_trac(self, prjid):
        tracadminpath, tracenvpath, svnrepopath = self._get_paths(prjid)
        tracconffile = os.path.join(tracenvpath, 'conf', 'trac.ini')
        tracconfig = config.Config(tracconffile)
        f = open(os.path.join(clue.app.__path__[0],
                              'skel', 'trac.ini.template'))
        data = f.read()
        f.close()
        pb = utils.PathBuilder(self._workingdir)
        dbpath = pb(os.path.join('etc', 'cluemapper', 'cluemapper.db'))
        ini = data % {'auth_file': self._cluemapperconfig['base']['auth_file'],
                      'shared_db': 'sqlite:%s' % dbpath}
        tracconfig.update_from_string(ini)
        tracconfig.save()

    def setup_default_trac(self, prjid):
        tracadminpath, tracenvpath, svnrepopath = self._get_paths(prjid)

        # running this twice because sometimes upgrade processing by
        # components overwrite our default values and we want them back
        self._setup_default_trac(prjid)
        self._execute([tracadminpath, tracenvpath, 'upgrade'])
        self._setup_default_trac(prjid)
        return 0
