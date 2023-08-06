import pylons
from tg2testapp.lib.base import BaseController
from tg import expose, flash
from pylons.i18n import ugettext as _
from tg import redirect, validate
from tw.forms.fields import PasswordField
from formencode.validators import FieldsMatch
from formencode import Schema

from tg2testapp.model import User, metadata
from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
from dbsprockets.saprovider import SAProvider
from dbsprockets.primitives import make_form, make_table, get_table_value

required_fields = ['password', 'user_name', 'email_address']
limit_fields  = ['user_name', 'display_name', 'email_address', 'password', ]

additional_fields = {'password_validation':PasswordField('password_verification', label_text='Verify'),}
form_validator =  Schema(chained_validators=(FieldsMatch('password',
                                                        'password_verification',
                                                        messages={'invalidNoMatch':
                                                                  "Passwords do not match"}),))

registrationForm = make_form(User,
                            'registration',
                            required_fields=required_fields,
                            limit_fields=limit_fields,
                            additional_fields=additional_fields,
                            form_validator=form_validator)
usersTable       = make_table(User, '/', omitted_fields=['user_id', 'created', 'password'])
loginForm        = make_form (User, identifier='myLoginForm', action='/login', limit_fields=['user_name', 'password'])

class RootController(BaseController):

    dbmechanic = DBMechanic(SAProvider(metadata), '/dbmechanic')

    @expose('sprockets.templates.index')
    def index(self):
        from datetime import datetime
        flash(_("Your application is now running"))
        return dict(now=datetime.now())

    @expose('genshi:sprockets.templates.register')
    def register(self, **kw):
        pylons.c.w.form = registrationForm
        return dict(value=kw)

    @validate(registrationForm, error_handler=register)
    def registration(self, **kw):
        raise redirect('/')


    @expose('genshi:sprockets.templates.register')
    def users(self):
        pylons.c.w.form = usersTable
        value = get_table_value(User)
        return dict(value=value)

    @expose('genshi:sprockets.templates.register')
    def login(self, **kw):
        pylons.c.w.form = loginForm
        return dict(value=kw)
