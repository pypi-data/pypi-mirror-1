import datetime
import optparse
import os
import pkg_resources
import sys
import zipfile
from clue.app import config
from clue.app import project
from clue.app import utils
from clue.secure import htpasswd


USAGE = """%prog <cmd> [extra_args]

  <cmd> has to be either 'create' or 'default_trac' currently

    create <project_name>
    default_trac <project_id>
    reset_perms <project_id>
    fix_paths <project_id>
    upgrade
    addmanager [<username>] [<password>]

Examples:
  %prog create 'My Project' myproj
  %prog default_trac myproj"""


class _AdminProjectManager(project.ProjectManager):
    """A security-less project manager implementation.

      >>> pm = _AdminProjectManager(None, None)
      >>> pm._can_manage()
      True
      >>> print pm._cluemapperconfig
      None
      >>> print pm._workingdir
      None
    """

    def __init__(self, cluemapperconfig, workingdir):
        self._admin_cluemapperconfig = cluemapperconfig
        self._admin_workingdir = workingdir
        project.ProjectManager.__init__(self, {}, {})

    @property
    def _cluemapperconfig(self):
        return self._admin_cluemapperconfig

    @property
    def _workingdir(self):
        return self._admin_workingdir

    def _can_manage(self):
        return True

    def _can_access(self, prjid):
        return True


class AdminError(Exception):
    pass


class AdminRunner(object):
    """Console script for running the admin module.

    First setup some mock values for our test setup.

      >>> from clue.tools.testing import Mock
      >>> def exit(val):
      ...     print 'exit: '+str(val)
      >>> exiter = Mock(exit=exit)
      >>> class MockLogger(object):
      ...     def info(self, msg): print 'info: '+msg
      ...     def error(self, msg): print 'error: '+msg
      >>> r = AdminRunner()
      >>> r.exiter = Mock(exit=exit)
      >>> r.logger = MockLogger()
      >>> r.config_loader = lambda x: None
      >>> r.usage = 'USAGE: justtesting'

    Trying to run the runner now will yield a problem with no workingdir.

      >>> r.console_run([])
      error: Working directory must be specified, please use the -w option
      1

    So we set the workingdir.

      >>> r.workingdir = 'foo'

    Running the runner with no args will give us standard usage output.

      >>> r.console_run([])
      Usage: justtesting
      ...
      exit: 0

    Creating a project with no errors runs as expected.

      >>> class MockPM(object):
      ...     _lastlog = 'nada'
      ...     def __init__(self, cluemapperconfig, workingdir): pass
      ...     def create_project(self, name): return Mock(prjid=name)
      ...     def setup_default_trac(self, prjid):
      ...         print 'setup project %r' % prjid
      ...     def reset_perms(self, prjid): print 'reset perms %r' % prjid
      >>> r.project_manager_factory = MockPM
      >>> r.console_run(['create', 'foo'])
      info: Successfully created project 'foo' with id 'foo'
      exit: 0

    Of course if the project creation raises a ProjectError, the runner
    will intercept and handle gently.

      >>> def bad_create_project(self, name): raise project.ProjectError('bah')
      >>> MockPM.create_project = bad_create_project
      >>> r.console_run(['create', 'foo'])
      error: bah
      error: Last command output was:
      nada
      exit: 1

    Initializing default arguments should run fine.

      >>> r.console_run(['default_trac', 'foo'])
      setup project 'foo'
      exit: 0

    Same as resetting permissions.

      >>> r.console_run(['reset_perms', 'foo'])
      reset perms 'foo'
      exit: 0

    Running an invalid command will give us standard usage.

      >>> r.console_run(['nosuchcmd', 'foo'])
      Usage: justtesting
      ...
      exit: 0

    """

    usage = USAGE
    exiter = sys
    project_manager_factory = _AdminProjectManager
    logger = utils.setup_logger()

    config_loader = staticmethod(config.load_config)

    def __init__(self):
        dist = pkg_resources.get_distribution('ClueMapper')
        self.version = dist.version

    def console_run(self, cmdargs=sys.argv[1:]):
        parser = optparse.OptionParser(usage=self.usage)
        parser.add_option('-w', '--workingdir', action='store',
                          dest='workingdir',
                          help='working directory, must contain base '
                               'of server')
        (options, args) = parser.parse_args(args=cmdargs)
        workingdir = getattr(options, 'workingdir', None) or \
                     getattr(self, 'workingdir', None)

        if not workingdir:
            self.logger.error('Working directory must be specified, '
                              'please use the -w option')
            return 1

        workingdir = os.path.realpath(os.path.abspath(workingdir))

        if len(args) == 0:
            parser.print_help()
            return self.exiter.exit(0)

        cmd = args[0]
        if cmd == 'create':
            prjname = args[1]
            cluemapperconfig = self.config_loader(workingdir)
            pmanager = self.project_manager_factory(cluemapperconfig,
                                                    workingdir)
            try:
                prj = pmanager.create_project(prjname)
                self.logger.info('Successfully created project %r with id %r'
                                 % (prjname, prj.prjid))
            except project.ProjectError, err:
                self.logger.error(str(err))
                if pmanager._lastlog is not None:
                    self.logger.error('Last command output was:\n%s'
                                      % pmanager._lastlog)
                return self.exiter.exit(1)
        elif cmd == 'default_trac':
            prjid = args[1]
            cluemapperconfig = self.config_loader(workingdir)
            pmanager = self.project_manager_factory(cluemapperconfig,
                                                    workingdir)
            pmanager.setup_default_trac(prjid)
        elif cmd == 'reset_perms':
            prjid = args[1]
            cluemapperconfig = self.config_loader(workingdir)
            pmanager = self.project_manager_factory(cluemapperconfig,
                                                    workingdir)
            pmanager.reset_perms(prjid)
        elif cmd == 'fix_paths':
            cluemapperconfig = self.config_loader(workingdir)
            pmanager = self.project_manager_factory(cluemapperconfig,
                                                    workingdir)
            for prjid in expand_projects(pmanager, *args[1:]):
                self.logger.info('Fixing paths for: %s' % prjid)
                pmanager.fix_paths(prjid)
        elif cmd == 'upgrade':
            self.cmd_upgrade(workingdir)
        elif cmd == 'export':
            self.cmd_export(workingdir, args[1:])
        elif cmd == 'import':
            self.cmd_import(workingdir, args[1:])
        elif cmd == 'addmanager':
            self.cmd_addmanager(workingdir, args[1:])
        else:
            parser.print_help()

        return self.exiter.exit(0)

    def cmd_addmanager(self, workingdir, args):
        cluemapperconfig = self.config_loader(workingdir)
        pb = utils.PathBuilder(workingdir)
        f = pb(os.path.join('etc', 'cluemapper', 'cluemapper.passwd'))
        passwdfile = htpasswd.HtpasswdFile(f, (not os.path.exists(f)))

        mgrs = cluemapperconfig['base'].get('managers', '')
        mgrs = set([x.strip() for x in mgrs.split(',')])

        username = None
        password = None
        if len(args) > 0:
            username = args[0]

        while username is None:
            sys.stdout.write('Username: ')
            sys.stdout.flush()
            username1 = sys.stdin.readline().strip()
            if not username1:
                print 'Please enter a username'
            else:
                username = username1

        while password is None:
            sys.stdout.write('Password: ')
            sys.stdout.flush()
            password1 = sys.stdin.readline().strip()
            sys.stdout.write('Confirm Password: ')
            sys.stdout.flush()
            password2 = sys.stdin.readline().strip()
            if password1 != password2:
                print "Passwords do not match, please try again"
            else:
                password = password1

        passwdfile.update(username, password)

        mgrs.add(username)
        cluemapperconfig['base']['managers'] = ','.join(sorted(mgrs))

        passwdfile.save()
        cluemapperconfig.save()

    def cmd_upgrade(self, workingdir):
        cluemapperconfig = self.config_loader(workingdir)
        authz = cluemapperconfig['base'].get('svnauthzfile', None)
        if not authz:
            pb = utils.PathBuilder(workingdir)
            authz = pb(os.path.join('etc', 'cluemapper',
                                    'svnauthzfile.conf'))
            cluemapperconfig['base']['svnauthzfile'] = authz
        for sectionname in cluemapperconfig.keys():
            section = cluemapperconfig[sectionname]
            if 'svnrepo' in section:
                del section['svnrepo']

            # fix relative paths
            for check in ('tracenv', 'tracenv_base', 'svnrepo_base',
                          'auth_file'):
                if check in section:
                    p = os.path.realpath(os.path.abspath(section[check]))
                    if p.startswith(workingdir):
                        section[check] = p[len(workingdir)+1:]

        pmanager = self.project_manager_factory(cluemapperconfig,
                                                workingdir)
        for prj in pmanager.projects:
            tracconf = pmanager.get_trac_config(prj.prjid)
            if 'szpm' in tracconf:
                for k, v in tracconf['szpm'].items():
                    tracconf['cluemapper'][k] = v
                del tracconf['szpm']
            tracconf['user_manager']['user_store'] = 'ClueMapperUserStore'
            tracconf['user_manager']['attribute_provider'] = \
                'ClueMapperAttributeProvider'
            if 'svnauthzfile' not in tracconf['cluemapper']:
                tracconf['cluemapper']['svnauthzfile'] = authz

            if 'szpmtrac.*' in tracconf['components']:
                del tracconf['components']['szpmtrac.*']
                tracconf['components']['clue.*'] = 'enabled'
            tracconf.save()

        cluemapperconfig.save()
        self.logger.info('Successfully upgraded for ClueMapper v%s' % self.version)

    def cmd_import(self, workingdir, args):
        cluemapperconfig = self.config_loader(workingdir)
        pmanager = self.project_manager_factory(cluemapperconfig,
                                                workingdir)
        z = zipfile.ZipFile(args[0])
        targetprjid = None
        if len(args) > 1:
            targetprjid = args[1]

        prjid = None
        for x in z.namelist():
            parts = x.split(os.path.sep, 2)
            if prjid is not None and parts[0] != prjid:
                raise AdminError('Found multiple directories')
            prjid = parts[0]
        if os.path.join(prjid, 'cluemapper-project.ini') not in z.namelist():
            raise AdminError('No cluemapper.ini present in correct place')

        if not targetprjid:
            targetprjid = prjid
        
        if targetprjid in [x.prjid for x in pmanager.projects]:
            raise AdminError('Project with prjid "%s" already exists'
                             % targetprjid)

        if targetprjid != prjid:
            self.logger.info('Importing %s as %s' % (prjid, targetprjid))
        else:
            self.logger.info('Importing %s' % prjid)

        prjdata = z.read(os.path.join(prjid, 'cluemapper-project.ini'))
        c = config.Config()
        c.update_from_string(prjdata)
        projectconfig = cluemapperconfig['project:'+targetprjid]
        projectconfig.update(c['project:'+prjid])

        relsvnrepo = os.path.join(prjid, 'svnrepo')
        reltracenv = os.path.join(prjid, 'tracenv')
        pb = utils.PathBuilder(workingdir)
        tracenv = os.path.join(pb(cluemapperconfig['base']['tracenv_base']),
                               targetprjid)
        svnrepo = os.path.join(pb(cluemapperconfig['base']['svnrepo_base']),
                               targetprjid)

        projectconfig['tracenv'] = tracenv[len(workingdir)+1:]

        self.logger.info('  extracting files to import')
        for x in z.namelist():
            if x.startswith(relsvnrepo):
                relfname = x[len(relsvnrepo)+1:]
                fname = os.path.join(svnrepo, relfname)
                if not os.path.isdir(os.path.dirname(fname)):
                    os.makedirs(os.path.dirname(fname))
                f = open(fname, 'wb')
                f.write(z.read(x))
                f.close()
            elif x.startswith(reltracenv):
                relfname = x[len(reltracenv)+1:]
                fname = os.path.join(tracenv, relfname)
                if not os.path.isdir(os.path.dirname(fname)):
                    os.makedirs(os.path.dirname(fname))
                f = open(fname, 'wb')
                f.write(z.read(x))
                f.close()

        z.close()

        self.logger.info('  updating trac.ini')
        c = config.Config(os.path.join(tracenv, 'conf', 'trac.ini'))
        c['trac']['repository_dir'] = svnrepo
        c['account-manager']['password_file'] = \
            pb(cluemapperconfig['base']['auth_file'])
        c['cluemapper']['database'] = 'sqlite:' + \
            os.path.join(workingdir, 'etc', 'cluemapper', 'cluemapper.db')
        c['cluemapper']['svnauthzfile'] = \
            pb(cluemapperconfig['base']['svnauthzfile'])
        c.save()

        pmanager.upgrade_project(targetprjid)

        cluemapperconfig.save()

        if targetprjid != prjid:
            self.logger.info('Successfully imported %s as %s'
                             % (prjid, targetprjid))
        else:
            self.logger.info('Successfully imported %s' % prjid)

    def cmd_export(self, workingdir, args):
        cluemapperconfig = self.config_loader(workingdir)
        pmanager = self.project_manager_factory(cluemapperconfig,
                                                workingdir)
        if '*' in args:
            projects = pmanager.projects
        else:
            projects = [pmanager.get_project(x) for x in args]

        today = datetime.date.today()
        datesuffix = '%s-%s-%s' % (today.year, today.month, today.day)
        for project in projects:
            zipfname = '%s-%s.zip' % (project.prjid, today)
            self.logger.info('Exporting %s into %s' % (project.prjid,
                                                       zipfname))

            z = zipfile.ZipFile(zipfname, 'w')

            prjconfig = config.Config()
            key = 'project:'+project.prjid
            prjconfig[key].update(cluemapperconfig[key])
            if 'tracenv' in prjconfig[key]:
                del prjconfig[key]['tracenv']
            z.writestr(os.path.join(project.prjid, 'cluemapper-project.ini'),
                       prjconfig.pretty_string())

            tracconffile = os.path.join(project.tracpath, 'conf', 'trac.ini')
            tracconf = config.Config(tracconffile)

            self.logger.info('  getting trac env')
            self._zip(z, project.tracpath, 'tracenv')
            self.logger.info('  getting svn repo')
            self._zip(z, tracconf['trac']['repository_dir'], 'svnrepo')

            self.logger.info('Successfully exported %s into %s'
                             % (project.prjid, zipfname))

            z.close()

    def _zip(self, z, start, suffix):
        for dirpath, dirnames, filenames in os.walk(start):
            basepath = dirpath[len(start)+1:]
            relpath = os.path.join(os.path.basename(start), suffix)
            if basepath:
                relpath = os.path.join(relpath, basepath)
            self.logger.debug('Creating '+relpath)
            for f in filenames:
                full = os.path.join(dirpath, f)
                zipfull = os.path.join(relpath, f)
                z.write(full, zipfull)

_runner = AdminRunner()


def expand_projects(pmanager, *prjids):
    """Generate a *set* of project ids fully globbing asterisk if found.

      >>> class Mock(object):
      ...     def __init__(self, **kw): self.__dict__.update(kw)
      >>> pmanager = Mock(projects=[Mock(prjid='foo'),
      ...                           Mock(prjid='bar'),
      ...                           Mock(prjid='abc')])
      >>> expand_projects(pmanager, 'foo', 'bar')
      set(['foo', 'bar'])
      >>> expand_projects(pmanager, 'foo', '*')
      set(['foo', 'bar', 'abc'])

    """
    res = set()
    for prjid in prjids:
        prjid = prjid.strip()
        if prjid == '*':
            res = set([x.prjid for x in pmanager.projects])
            return res
        res.add(prjid)
    return res


def main(args=[]):
    cmdargs = args + sys.argv[1:]
    try:
        _runner.console_run(cmdargs)
    except AdminError, err:
        _runner.logger.error(str(err))
