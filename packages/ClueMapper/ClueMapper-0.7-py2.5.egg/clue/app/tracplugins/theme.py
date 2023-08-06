from pkg_resources import resource_filename

from trac import core as traccore
from trac.admin import api as adminapi
from trac.web import chrome
from trac.util.translation import _

from clue.app import project
from clue.app import utils
from clue.themer import theme


class ThemeAdminPanel(traccore.Component):
    traccore.implements(adminapi.IAdminPanelProvider,
                        chrome.ITemplateProvider)

    def get_admin_panels(self, req):
        if req.perm.has_permission('TRAC_ADMIN'):
            yield ('general', _('General'), 'themeconfig', 'Theme')

    def render_admin_panel(self, req, cat, page, path_info):
        tmanager = theme.ThemeManager(req.environ['cluemapper.workingdir'],
                                      req.environ['cluemapper.config'])
        pmanager = project.ProjectManager(req.environ)
        prjid = utils.get_prjid(req.environ)
        themeid = pmanager.get_project_theme(prjid)
        if not themeid:
            themeid = tmanager.default_theme.themeid

        data = {'themes': tmanager.themes,
                'currentthemeid': themeid}
        if req.args.get('applied', False):
            themeid = req.args['__clue_set_themeid']
            fields = {'theme': themeid}
            pmanager.update_project(prjid, fields)
            data['message'] = 'Settings saved'
            data['currentthemeid'] = themeid

        return 'admin-themeconfig.html', data

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('cluemapperthemer', resource_filename(__name__, 'htdocs'))]
