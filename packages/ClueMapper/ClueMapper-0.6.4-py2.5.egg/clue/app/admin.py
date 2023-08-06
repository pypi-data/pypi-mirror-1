import os
import sys
import optparse
from clue.app import config
from clue.app import project
from clue.app import utils

USAGE = """%prog <cmd> [extra_args]

  <cmd> has to be either 'create' or 'default_trac' currently

    create <project_name>
    default_trac <project_id>
    reset_perms <project_id>
    fix_paths <project_id>
    upgrade

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
            cluemapperconfig = self.config_loader(workingdir)
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

                if 'szpmtrac.*' in tracconf['components']:
                    del tracconf['components']['szpmtrac.*']
                    tracconf['components']['clue.*'] = 'enabled'
                tracconf.save()

            cluemapperconfig.save()
            self.logger.info('Successfully upgraded ClueMapper')
        else:
            parser.print_help()

        return self.exiter.exit(0)


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
    _runner.console_run(cmdargs)
