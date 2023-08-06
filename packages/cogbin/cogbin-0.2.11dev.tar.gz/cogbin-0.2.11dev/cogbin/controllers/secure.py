"""Test Secure Controller"""
from cogbin.lib.base import BaseController
from tg import expose, flash
from pylons.i18n import ugettext as _
#from tg import redirect, validate
#from cogbin.model import DBSession, metadata
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider
from repoze.what.predicates import has_permission


class SecureController(BaseController):
    """Sample controller-wide authorization"""

    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission('manage',
                                msg=_('Only for people with the "manage" permission'))

    @expose('cogbin.templates.index')
    def index(self):
        flash(_("Secure Controller here"))
        return dict(page='index')

    @expose('cogbin.templates.index')
    def some_where(self):
        """should be protected because of the require attr
        at the controller level.
        """
        return dict(page='some_where')
