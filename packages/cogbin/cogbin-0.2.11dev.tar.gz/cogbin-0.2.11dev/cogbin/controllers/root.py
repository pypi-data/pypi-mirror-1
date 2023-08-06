"""Main Controller"""
from cogbin.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _
#from tg import redirect, validate
from cogbin.model import DBSession, metadata
from cogbin.controllers.error import ErrorController
from cogbin import model
from catwalk.tg2 import Catwalk
from repoze.what import predicates
from cogbin.controllers.secure import SecureController
#Cogbin specific
from cogbin.model.pypi import PyPIPackages
import pylons


#TGRUM Admin interface
from tg import config
from tgrum import RumAlchemyController

# This is the predicate that we'll use to secure the Rum app
is_manager = predicates.has_permission(
    'manage',
    msg=_('Only for people with the "manage" permission')
)

#cogbin data grid
from tw.forms.datagrid import DataGrid
from genshi import Markup

def get_link(item):
    return Markup("""<a href="%s">%s</a>""" % (item.home_page,item.name))
def get_link2(item):
    return Markup("""<a href="http://pypi.python.org/pypi/%s/%s">%s</a>""" % (item.name,item.version,item.version))

cogbin_grid = [('Package Name',get_link),
                ('Version',get_link2),
                ('Summary','summary'),
                ('Author','author'),
                #('Keywords','keywords'),
                ('Description','description'),
                #('Zip Code','ZipCode'),
                #('Gender','Gender')
                ]


class RootController(BaseController):
    #admin = Catwalk(model, DBSession)
    admin = RumAlchemyController(
        model,
        is_manager,
        template_path=config['paths']['templates'][0],
        # Since this TG's master template will render it
        render_flash=False,
        )

    error = ErrorController()

    @expose('cogbin.templates.index')
    def index(self):
        #Categories. Need to move to app config.
        categories={}
        categories['turbogears ']=''
        categories['turbogears.application']=''
        categories['turbogears.command']=''
        categories['turbogears.extension']=''
        categories['turbogears.widgets']=''
        categories['python.templating.engines']=''
        categories['turbogears.identity.provider']=''
        categories['turbogears2 ']=''
        categories['turbogears2.application']=''
        categories['turbogears2.identity.provider']=''
        categories['turbogears2.widgets']=''
        categories['turbogears2.command']=''
        #Get data from database
        for category in [ (k) for k in sorted(categories.keys())]:
            categories[category]=DBSession.query(PyPIPackages).filter(PyPIPackages.keywords.like('%'+category+'%'))        
        #Fill datagrid with the data and pass it to tmpl_context.
        pylons.c.cogbin_grid=DataGrid(fields = cogbin_grid)
        pylons.c.cogbin_data=categories

        return dict(page='Cogbin')

    @expose('cogbin.templates.about')
    def about(self):
        return dict(page='about')

    @expose('cogbin.templates.authentication')
    def auth(self):
        return dict(page='auth')

    @expose('cogbin.templates.index')
    @require(predicates.has_permission('manage', msg=_('Only for managers')))
    def manage_permission_only(self, **kw):
        return dict(page='managers stuff')
    
    @expose('cogbin.templates.index')
    @require(predicates.has_permission('manage', msg=_('Only for managers')))
    def manage_cogbin(self, **kw):
        return dict(page='PyPIPackages Manage')

    @expose('cogbin.templates.index')
    @require(predicates.is_user('editor', msg=_('Only for the editor')))
    def editor_user_only(self, **kw):
        return dict(page='editor stuff')

    @expose('cogbin.templates.login')
    def login(self, came_from=url('/')):
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        flash(_('We hope to see you soon!'))
        redirect(came_from)
