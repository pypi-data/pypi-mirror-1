# -*- coding: utf-8 -*-

from pickle import dumps, loads
from base64 import b64encode, b64decode
from time import time
from smtplib import SMTP

from Crypto.Cipher import Blowfish

from logilab.common.decorators import clear_cache

from cubicweb.common import tags, mail
from cubicweb.view import StartupView
from cubicweb.web import Redirect, ValidationError
from cubicweb.web import (controller, httpcache, form,
                          formwidgets as wdg, formfields as ff)
from cubicweb.web.views import forms, basecomponents, urlrewrite

from cubes.registration import captcha


_CYPHERERS = {}
def _cypherer(seed):
    try:
        return _CYPHERERS[seed]
    except KeyError:
        _CYPHERERS[seed] = Blowfish.new(seed, Blowfish.MODE_ECB)
        return _CYPHERERS[seed]


def encrypt(data, seed):
    string = dumps(data)
    string = string + '*' * (8 - len(string) % 8)
    string = b64encode(_cypherer(seed).encrypt(string))
    return unicode(string)


def decrypt(string, seed):
    # pickle ignores trailing characters so we do not need to strip them off
    string = _cypherer(seed).decrypt(b64decode(string))
    return loads(string)


class CaptchaView(StartupView):
    http_cache_manager = httpcache.NoHTTPCacheManager
    id = 'captcha'
    binary = True
    templatable = False
    content_type = 'image/jpg'

    def call(self):
        text, data = captcha.captcha(self.config['captcha-font-file'],
                                     self.config['captcha-font-size'])
        self.req.set_session_data('captcha', text)
        self.w(data.read())


class CaptchaWidget(wdg.TextInput):
    def render(self, form, field):
        name, curvalues, attrs = self._render_attrs(form, field)
        # t=int(time()*100) to make sure img is not cached
        src = form.req.build_url('view', vid='captcha', t=int(time()*100))
        img = tags.img(src=src, alt=u'captcha')
        img = u'<div class="captcha">%s</div>' % img
        return img + super(CaptchaWidget, self).render(form, field)


class RegistrationForm(forms.FieldsForm):
    id = 'registration'
    form_buttons = [wdg.SubmitButton()]

    @property
    def action(self):
        return self.req.build_url(u'registration_sendmail')

    login = ff.StringField(widget=wdg.TextInput(), required=True)
    upassword = ff.StringField(widget=wdg.PasswordInput(), required=True)
    use_email = ff.StringField(widget=wdg.TextInput(), required=True)
    firstname = ff.StringField(widget=wdg.TextInput())
    surname = ff.StringField(widget=wdg.TextInput())
    captcha = ff.StringField(widget=CaptchaWidget(), required=True,
                             label=_('captcha'),
                             help=_('please copy the letters from the image'))


class RegistrationFormView(form.FormViewMixIn, StartupView):
    id = 'registration'

    def call(self):
        form = self.vreg.select_object('forms', 'registration', self.req)
        self.w(form.form_render())


class RegistrationSendMailController(controller.Controller):
    id = 'registration_sendmail'
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
        self.config.sendmails([(msg, (recipient,))])
        raise Redirect(self.success_redirect_url())

    def checked_data(self):
        '''only basic data check here (required attributes and password
        confirmation check)
        '''
        fieldsform = self.vreg.select_object('forms', 'registration', self.req)
        data = {}
        errors = {}
        for field in fieldsform._fields_:
            value = self.req.form.get(field.name, u'').strip()
            if not value:
                if field.required:
                    errors[field.name] = self.req._('required attribute')
            data[field.name] = value
        if data['upassword'] != self.req.form.get('upassword-confirm'):
            errors['upassword'] = _('passwords are different')
        captcha = self.req.get_session_data('captcha', None, pop=True)
        if data['captcha'].lower() != captcha.lower():
            errors['captcha'] = self.req._('incorrect captcha value')
        if errors:
            raise ValidationError(None, errors)
        return data

    def build_email(self, recipient, data):
        if not data.get('firstname') or data.get('surtname'):
            data['firstname'] = data['login']
        data.update({'base_url': self.config['base-url'],
                    'url': self.activation_url(data)})
        content = self.req._(self.content) % data
        subject = self.req._(self.subject) % data
        return mail.format_mail({}, [recipient], content=content,
                                subject=subject, config=self.config)

    def activation_url(self, data):
        key = encrypt(data, self.config['cypher-seed'])
        return self.build_url('registration_confirm', key=key)

    def success_redirect_url(self):
        msg = self.req._(u'Your registration email has been sent. Follow '
                         'instructions in there to activate your account.')
        return self.build_url('', __message=msg)


class RegistrationConfirmController(controller.Controller):
    id = 'registration_confirm'

    def publish(self, rset=None):
        req = self.req
        try:
            data = decrypt(req.form['key'], self.vreg.config['cypher-seed'])
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
        return self.build_url(u'register', **data)

    def success_redirect_url(self, data):
        msg = self.req._(u'Congratulations, your registration is complete. '
                         'Welcome %(firstname)s %(surname)s !')
        return self.build_url('', __message=msg%data)


class UserLink(basecomponents.UserLink):
    def anon_user_link(self):
        super(UserLink, self).anon_user_link()
        self.w(u'&nbsp;[<a class="logout" href="%s">%s</a>]' % (
            self.build_url('register'), self.req._('i18n_register_user')))

## urls #######################################################################

class RegistrationSimpleReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/register', dict(vid='registration')),
        ]

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (UserLink,))
    vreg.register_and_replace(UserLink, basecomponents.UserLink)
