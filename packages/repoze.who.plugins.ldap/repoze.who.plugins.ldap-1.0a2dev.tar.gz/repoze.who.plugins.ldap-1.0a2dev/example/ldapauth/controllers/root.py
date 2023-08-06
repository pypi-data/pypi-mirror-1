"""Main Controller"""
from ldapauth.lib.base import BaseController
from tg import expose, flash
from pylons.i18n import ugettext as _
#from tg import redirect, validate
#from ldapauth.model import DBSession, metadata
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider

class RootController(BaseController):
    #admin = DBMechanic(SAProvider(metadata), '/admin')

    @expose('ldapauth.templates.index')
    def index(self):
        return dict(page='index')

    @expose('ldapauth.templates.about')
    def about(self):
        return dict(page='about')

