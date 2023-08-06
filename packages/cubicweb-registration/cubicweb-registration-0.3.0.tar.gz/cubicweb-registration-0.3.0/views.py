from logilab.common.decorators import clear_cache

from cubicweb import mail, crypto
from cubicweb.view import StartupView
from cubicweb.web import Redirect, ValidationError
from cubicweb.web import controller, form, captcha
from cubicweb.web import formwidgets as fw, formfields as ff
from cubicweb.web.views import forms, basecomponents, urlrewrite



class RegistrationForm(forms.FieldsForm):
    __regid__ = 'registration'
    domid = 'registrationForm'
    form_buttons = [fw.SubmitButton()]

    @property
    def action(self):
        return self._cw.build_url(u'registration_sendmail')

    login = ff.StringField(widget=fw.TextInput(), required=True)
    upassword = ff.StringField(widget=fw.PasswordInput(), required=True)
    use_email = ff.StringField(widget=fw.TextInput(), required=True)
    firstname = ff.StringField(widget=fw.TextInput())
    surname = ff.StringField(widget=fw.TextInput())
    captcha = ff.StringField(widget=captcha.CaptchaWidget(), required=True,
                             label=_('captcha'),
                             help=_('please copy the letters from the image'))


# XXX move captcha validation to a CaptchaField

class RegistrationFormView(form.FormViewMixIn, StartupView):
    __regid__ = 'registration'

    def call(self):
        form = self._cw.vreg['forms'].select('registration', self._cw)
        self.w(form.render(display_progress_div=False))


class RegistrationSendMailController(controller.Controller):
    __regid__ = 'registration_sendmail'
    content = _(u'''
Hello %(firstname)s %(surname)s,

thanks for registering on %(base_url)s.

Please click on the link below to activate your account :
%(url)s.

See you soon on %(base_url)s !
''')
    subject = _(u'Confirm your registration on %(base_url)s')

    def publish(self, rset=None):
        data = self.checked_data()
        recipient = data['use_email']
        msg = self.build_email(recipient, data)
        self._cw.vreg.config.sendmails([(msg, (recipient,))])
        raise Redirect(self.success_redirect_url())

    def checked_data(self):
        '''only basic data check here (required attributes and password
        confirmation check)
        '''
        fieldsform = self._cw.vreg['forms'].select('registration', self._cw)
        data = {}
        errors = {}
        for field in fieldsform._fields_:
            value = self._cw.form.get(field.name, u'').strip()
            if not value:
                if field.required:
                    errors[field.name] = self._cw._('required attribute')
            data[field.name] = value
        if data['upassword'] != self._cw.form.get('upassword-confirm'):
            errors['upassword'] = _('passwords are different')
        captcha = self._cw.get_session_data('captcha', None, pop=True)
        if captcha is None:
            errors[None] = self._cw._('unable to check captcha, please try again')
        elif data['captcha'].lower() != captcha.lower():
            errors['captcha'] = self._cw._('incorrect captcha value')
        if errors:
            raise ValidationError(None, errors)
        return data

    def build_email(self, recipient, data):
        if not data.get('firstname') or data.get('surtname'):
            data['firstname'] = data['login']
        data.update({'base_url': self._cw.vreg.config['base-url'],
                    'url': self.activation_url(data)})
        content = self._cw._(self.content) % data
        subject = self._cw._(self.subject) % data
        return mail.format_mail({}, [recipient], content=content,
                                subject=subject, config=self._cw.vreg.config)

    def activation_url(self, data):
        key = crypto.encrypt(data, self._cw.vreg.config['registration-cypher-seed'])
        return self._cw.build_url('registration_confirm', key=key)

    def success_redirect_url(self):
        msg = self._cw._(u'Your registration email has been sent. Follow '
                         'instructions in there to activate your account.')
        return self._cw.build_url('', __message=msg)


class RegistrationConfirmController(controller.Controller):
    __regid__ = 'registration_confirm'

    def publish(self, rset=None):
        req = self._cw
        try:
            data = crypto.decrypt(req.form['key'],
                                  req.vreg.config['registration-cypher-seed'])
            self.debug('registration data: %s', data)
        except:
            msg = req._(u'Invalid registration data. Please try registering again.')
            raise Redirect(req.build_url(u'register', __message=msg))
        login, password = data.pop('login'), data.pop('upassword')
        try:
            self.appli.repo.register_user(login, password, email=data['use_email'],
                                          firstname=data['firstname'],
                                          surname=data['surname'])
        except ValidationError, e:
            raise Redirect(self.failure_redirect_url(data, e.errors))
        req.form['__login'] = login
        req.form['__password'] = password
        clear_cache(req, 'get_authorization') # force new authentication (anon until there)
        if req.cnx:
            req.cnx.close()
        req.cnx = None
        try:
            self.appli.session_handler.set_session(req)
        except Redirect:
            pass
        assert req.user.login == login
        raise Redirect(self.success_redirect_url(data))

    def failure_redirect_url(self, data, errors):
        # be sure not to get a password in your redirect url
        data.pop('upassword', None)
        data.pop('upassword-confirm', None)
        data['__message'] = u'<br/>'.join(u'%s : %s' % (k,v)
                                          for (k,v) in errors.iteritems())
        return self._cw.build_url(u'register', **data)

    def success_redirect_url(self, data):
        msg = self._cw._(u'Congratulations, your registration is complete. '
                         'Welcome %(firstname)s %(surname)s !')
        return self._cw.build_url('', __message=msg%data)


class UserLink(basecomponents.UserLink):
    def anon_user_link(self):
        super(UserLink, self).anon_user_link()
        self.w(u'&nbsp;[<a class="logout" href="%s">%s</a>]' % (
            self._cw.build_url('register'), self._cw._('i18n_register_user')))

## urls #######################################################################

class RegistrationSimpleReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/register', dict(vid='registration')),
        ]

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (UserLink,))
    vreg.register_and_replace(UserLink, basecomponents.UserLink)
