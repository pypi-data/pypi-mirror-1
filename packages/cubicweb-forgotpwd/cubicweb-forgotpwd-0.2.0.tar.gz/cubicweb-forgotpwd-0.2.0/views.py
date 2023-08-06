"""cube-specific forms/views/actions/components

:organization: Logilab
:copyright: 2001-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

import random
import string
from datetime import datetime, timedelta

from yams import ValidationError

from logilab.mtconverter import xml_escape

from cubicweb.view import StartupView
from cubicweb.crypto import encrypt, decrypt
from cubicweb.web import (Redirect, controller, form, captcha,
                          formwidgets as wdg, formfields as ff)
from cubicweb.web.views import forms, urlrewrite, basetemplates

_ = unicode

# Login form
# ----------

class LogFormView(basetemplates.LogFormView):

    def login_form(self, id):
        super(LogFormView, self).login_form(id)
        self._cw.add_css('cubes.forgotpwd.css')
        self.w(u'<span class="forgotpwdLink"><a href="%s">%s</a></span>' % (
            xml_escape(self._cw.build_url('forgottenpassword')),
            self._cw._('Forgot your password ?')))

# First form, send an email
# -------------------------

class ForgottenPasswordForm(forms.FieldsForm):
    __regid__ = 'forgottenpassword'

    form_buttons = [wdg.SubmitButton()]
    @property
    def action(self):
        return self._cw.build_url(u'forgottenpassword_sendmail')

    use_email = ff.StringField(widget=wdg.TextInput(), required=True, label=_(u'your email address'))
    captcha = ff.StringField(widget=captcha.CaptchaWidget(), required=True,
                             label=_('captcha'),
                             help=_('please copy the letters from the image'))

class ForgottenPasswordFormView(form.FormViewMixIn, StartupView):
    __regid__ = 'forgottenpassword'

    def call(self):
        form = self._cw.vreg['forms'].select('forgottenpassword', self._cw)
        self.w(u'<p>%s</p>' % self._cw._(u'Forgot your password ?'))
        self.w(form.render())

class ForgottenPasswordSendMailController(controller.Controller):
    __regid__ = 'forgottenpassword_sendmail'

    def publish(self, rset=None):
        data = self.checked_data()
        try:
            self.appli.repo.forgotpwd_send_email(data)
        except ValidationError:
            raise
        except Exception, exc:
            msg = str(exc)
        else:
            msg = self._cw._(u'An email has been sent, follow instructions in there to change your password.')
        raise Redirect(self.build_url('pwdsent', __message=msg))

    def checked_data(self):
        '''only basic data check here (required attributes and password
        confirmation check)
        '''
        fieldsform = self._cw.vreg['forms'].select('forgottenpassword', self._cw)
        data = {}
        errors = {}
        for field in fieldsform._fields_:
            value = self._cw.form.get(field.name, u'').strip()
            if not value:
                if field.required:
                    errors[field.name] = self._cw._('required attribute')
            data[field.name] = value
        captcha = self._cw.get_session_data('captcha', None, pop=True)
        if captcha is None:
            errors[None] = self._cw._('unable to check captcha, please try again')
        elif data['captcha'].lower() != captcha.lower():
            errors['captcha'] = self._cw._('incorrect captcha value')
        if errors:
            raise ValidationError(None, errors)
        return data


class PasswordSentView(StartupView):
    __regid__ = 'pwdsent'

    def call(self):
        self.wview('index', self.cw_rset)

# Second form, ask for a new password
# -----------------------------------

class ForgottenPasswordRequestForm(forms.FieldsForm):
    __regid__ = 'forgottenpasswordrequest'

    form_buttons = [wdg.SubmitButton()]
    @property
    def action(self):
        return self._cw.build_url(u'forgottenpassword-requestconfirm')

    upassword = ff.StringField(widget=wdg.PasswordInput(), required=True)


class ForgottenPasswordRequestView(form.FormViewMixIn, StartupView):
    __regid__ = 'forgottenpasswordrequest'

    def check_key(self):
        try:
            return decrypt(self._cw.form['key'],
                           self._cw.vreg.config['forgotpwd-cypher-seed'])
        except:
            msg = self._cw._(u'Invalid link. Please try again.')
            raise Redirect(self._cw.build_url(u'forgottenpassword', __message=msg))

    def call(self):
        key = self.check_key()
        form = self._cw.vreg['forms'].select('forgottenpasswordrequest', self._cw)
        form.add_hidden('use_email', key['use_email'])
        form.add_hidden('revocation_id', key['revocation_id'])
        self.w(u'<p>%s</p>' % self._cw._(u'Update your password:'))
        self.w(form.render())


class ForgottenPasswordRequestConfirm(controller.Controller):
    __regid__ = 'forgottenpassword-requestconfirm'

    def publish(self, rset=None):
        data = self.checked_data()
        msg = self.appli.repo.forgotpwd_change_passwd(data)
        raise Redirect(self.build_url('pwdreset', __message=msg))

    def checked_data(self):
        cw = self._cw
        fieldsform = cw.vreg['forms'].select('forgottenpasswordrequest', cw)
        data = {}
        errors = {}
        for field in fieldsform.fields:
            value = cw.form.get(field.name, u'').strip()
            if not value and field.required:
                errors[field.name] = cw._('required attribute')
            data[field.name] = value
        data['use_email'] = cw.form.get('use_email', '').strip()
        data['revocation_id'] = cw.form.get('revocation_id', '').strip()
        if data['upassword'] != cw.form.get('upassword-confirm'):
            errors['upassword'] = _('passwords are different')
        if errors:
            raise ValidationError(None, errors)
        return data


class PasswordResetView(StartupView):
    __regid__ = 'pwdreset'

    def call(self):
        self.wview('index', self.rset)


# Monkey Patching
# ---------------

from cubicweb.server.repository import Repository
from logilab.common.decorators import monkeypatch
from cubicweb.mail import format_mail

@monkeypatch(Repository)
def forgotpwd_send_email(self, data):
    session = self.internal_session()
    revocation_limit = self.config['revocation-limit']
    revocation_id = u''.join([random.choice(string.letters+string.digits)
                              for x in xrange(10)])
    revocation_date = datetime.now() + timedelta(minutes=revocation_limit)
    try:
        existing_requests = session.execute('Any F WHERE U primary_email E, E address %(e)s, U has_fpasswd F',
                                            {'e': data['use_email']})
        if existing_requests:
            raise ValidationError(None, {None: session._('You have already asked for a new password.')})
        rset = session.execute('INSERT Fpasswd X: X revocation_id %(a)s, X revocation_date %(b)s, '
                               'U has_fpasswd X WHERE U primary_email E, E address %(e)s',
                               {'a':revocation_id, 'b':revocation_date, 'e': data['use_email']})
        if not rset:
            raise ValidationError(None, {None: session._(u'An error occured, this email address is unknown.')})
        data['revocation_id'] = revocation_id
        key = encrypt(data, session.vreg.config['forgotpwd-cypher-seed'])
        url = session.build_url('forgottenpasswordrequest', key=key)
        session.set_shared_data('resetlink', url)
        # mail is sent on commit
        session.commit()
    finally:
        session.close()

@monkeypatch(Repository)
def forgotpwd_change_passwd(self, data):
    session = self.internal_session()
    try:
        rset = session.execute('Any F, U WHERE U is CWUser, U primary_email E, E address %(email)s, EXISTS(U has_fpasswd F, F revocation_id %(revid)s)',
                               {'email': data['use_email'], 'revid':data['revocation_id']})
        if rset:
            forgotpwd = rset.get_entity(0,0)
            revocation_date = forgotpwd.revocation_date
            user = rset.get_entity(0,1)
            if revocation_date > datetime.now():
                session.execute('SET U upassword %(newpasswd)s WHERE U is CWUser, U eid %(usereid)s',
                                {'newpasswd':data['upassword'].encode('UTF-8'), 'usereid':user.eid})
                session.execute('DELETE Fpasswd F WHERE F eid %(feid)s',
                                {'feid':forgotpwd.eid})
                session.commit()
                msg = session._(u'Your password has been changed !')
            else:
                msg = session._(u'That link has either expired or is not valid.')
        else:
            msg = session._(u'You already changed your password. This link has expired.')
        return msg
    finally:
        session.close()

# URL rewriting
# -------------

class RegistrationSimpleReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/forgottenpassword', dict(vid='forgottenpassword')),
        ('/forgottenpasswordrequest', dict(vid='forgottenpasswordrequest')),
        ('/pwdsent', dict(vid='pwdsent')),
        ('/pwdreset', dict(vid='pwdreset')),
        ]

# Registration
# ------------

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (LogFormView,))
    vreg.register_and_replace(LogFormView, basetemplates.LogFormView)
