import os
from pkg_resources import resource_filename

from trac import core as traccore
from trac import config as tracconfig
from trac import perm
from trac.admin import api as adminapi
from trac.web import chrome
from trac.util.translation import _

from clue.app import project
from clue.app import config as clueconfig
from clue.app import utils
from clue.app.tracplugins import user as pluginuser


class NoAccessFileError(Exception):
    pass


def interpret_acl(access):
    read = False
    write = False
    if 'r' in access:
        read = True
    if 'w' in access:
        write = True
    return read, write


def _u(s):
    if not isinstance(s, unicode):
        return s.encode('utf-8')
    return s


def name_cmp(x, y):
    xname = x['fullname'].lower()
    if xname == 'anonymous':
        return -1
    yname = y['fullname'].lower()
    if yname == 'anonymous':
        return 1
    return cmp(xname, yname)


class SourceControl(traccore.Component):

    svnauthzfile = tracconfig.Option(
        'cluemapper', 'svnauthzfile',
        'svnauthzfile.conf',
        """Subversion authz file""")

    @property
    def prjid(self):
        return self.compmgr.path.split(os.path.sep)[-1]

    def get_users_with_access(self):
        if not self.svnauthzfile:
            raise NoAccessFileError('No cluemapper.svnauthzfile property has '
                                    'been set')

        if not os.path.exists(self.svnauthzfile):
            raise NoAccessFileError('The svnauthzfile file "%s" does not exist'
                                    % self.svnauthzfile)

        authz = clueconfig.Config(self.svnauthzfile)
        acl = authz[self.prjid+':/']

        return ((username, ) + interpret_acl(access)
                for username, access in acl.items()
                if not username.startswith('@'))

    def _update_access(self, authz, username, read, write):
        acl = authz[self.prjid+':/']
        updated = False
        if not read and not write and username in acl:
            del acl[username]
            updated = True
        else:
            rw = ''
            if read:
                rw += 'r'
            if write:
                rw += 'w'
            if acl.get(username, None) != rw:
                acl[username] = rw
                updated = True

        return updated

    def update_access(self, username, read, write):
        authz = clueconfig.Config(self.svnauthzfile)
        if self._update_access(authz, username, read, write):
            authz.save()

    def update_multiple_access(self, users):
        authz = clueconfig.Config(self.svnauthzfile)
        updated = False
        for username, read, write in users:
            updated = self._update_access(authz, username, read, write) \
                      or updated
        if updated:
            authz.save()


class SourceControlAdminPanel(traccore.Component):
    traccore.implements(adminapi.IAdminPanelProvider,
                        chrome.ITemplateProvider)

    def __init__(self, *args, **kwargs):
        traccore.Component.__init__(self, *args, **kwargs)
        self.sourcecontrol = SourceControl(self.compmgr)

    def get_admin_panels(self, req):
        if req.perm.has_permission('TRAC_ADMIN'):
            yield ('general', _('General'),
                   'sourcecontrol', 'Source Control')

    def apply_access(self, req):
        users = []
        for arg, value in req.args.items():
            if not arg.startswith('user_'):
                continue
            username = arg[5:]
            read = bool(req.args.get('read_'+username, False))
            write = bool(req.args.get('write_'+username, False))
            users.append((username, read, write))

        self.sourcecontrol.update_multiple_access(users)

    def apply_adduser(self, req):
        self.sourcecontrol.update_access(req.args['username'],
                                    bool(req.args.get('read', False)),
                                    bool(req.args.get('write', False)))

    def render_admin_panel(self, req, cat, page, path_info):
        message = None

        if req.args.get('noaccess_applied', False):
            self.apply_access(req)
            message = u'User access updated'
        if req.args.get('existing_applied', False):
            self.apply_access(req)
            message = u'User access updated'
        if req.args.get('adduser', False):
            self.apply_adduser(req)
            message = u'User added'

        pmanager = project.ProjectManager(req.environ)
        prjid = utils.get_prjid(req.environ)
        themeid = pmanager.get_project_theme(prjid)

        existing = []
        noaccess = []
        try:
            for x in self.get_user_access():
                if x['read'] or x['write']:
                    existing.append(x)
                else:
                    noaccess.append(x)
        except NoAccessFileError, err:
            message = str(err)

        data = {'existing_users': sorted(existing, name_cmp),
                'noaccess_users': sorted(noaccess, name_cmp),
                'message': message}

        return 'admin-sourcecontrol.html', data

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_user_access(self):
        sourcecontrol = SourceControl(self.compmgr)
        users = {'*': (False, False)}
        for username, read, write in sourcecontrol.get_users_with_access():
            users[username] = read, write

        userstore = pluginuser.ClueMapperUserStore(self.compmgr)
        permsys = perm.PermissionSystem(self.compmgr)
        for username in userstore.search_users():
            if not permsys.check_permission('WIKI_VIEW', username):
                continue

            if username not in users:
                users[username] = False, False

        provider = pluginuser.ClueMapperAttributeProvider(self.compmgr)
        for username, access in users.items():
            fullname = _u(username)
            if username == '*':
                fullname = u'anonymous'
            else:
                name = provider.get_user_attribute(username, 'name')
                if name:
                    fullname = u'%s (%s)' % (_u(name), _u(username))

            read, write = access
            yield {'username': username,
                   'fullname': fullname,
                   'read': read or None,
                   'write': write or None}

    def get_htdocs_dirs(self):
        return []
