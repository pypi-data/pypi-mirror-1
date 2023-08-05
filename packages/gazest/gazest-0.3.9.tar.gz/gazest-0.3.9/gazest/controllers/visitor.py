#  Copyright (C) 2007 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from gazest.lib.base import *

from authkit.permissions import NotAuthenticatedError, NotAuthorizedError
from authkit.permissions import RemoteUser, RequestPermission
from authkit.pylons_adaptors import authorize

from openid.store.filestore import FileOpenIDStore
from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure

from gazest.lib.formutil import *
from pprint import pprint
from datetime import datetime

import os

log = logging.getLogger(__name__)

class AuthValidator(validators.FormValidator):
    """used only to validate the authval of registration forms"""
    validate_partial_form = True

    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        try:
            if field_dict["regtype"] == "email":
                vtor = validators.Email()
                field_dict["regval"] = vtor.to_python(field_dict["regval"])
            else:
                vtor = OpenIDValidator()
                field_dict["regval"] = vtor.to_python(field_dict["regval"])
        except validators.Invalid, e:
            raise validators.Invalid(
                str(e), 
                field_dict["regval"], 
                state, 
                error_dict=dict(regval=str(e)))


class LoginEmailPasswordValidator(validators.FormValidator):
    """Check the password when login by with email."""
    validate_partial_form = True

    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        user = model.User.query.selectfirst_by(email=field_dict["email"], 
                                        status="active")
        if not user.check_password(field_dict["password"]):
                raise validators.Invalid(
                    "Invalid password or email address", 
                    field_dict["email"], 
                    state)


class UniqueUser(validators.FormValidator):
    """Used only in registration forms.

    The user can in fact exist, if it is pending and has the same authval, 
    a new confirmation request will be created.
    """
    validate_partial_form = True

    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        user = model.User.query.selectfirst_by(username=field_dict["username"])

        if user:
            if user.status != "conf_pending":
                msg = "This username is already taken"
                raise validators.Invalid(
                    msg, 
                    field_dict["username"], 
                    state, 
                    error_dict=dict(username=msg))
            authval = user.authtype == "email" and user.email or user.openid

            # don't need to check reg type, syntax imply type
            if user.status == "conf_pending" \
                    and authval != field_dict["regval"]:
                # TODO: all the conf might be expired, now would be a
                # good time to put this name back in the pool if it is
                # so
                msg =("This username is pending confirmation."
                "  If you submitted the first request, retry with the same "
                "  informations to reactivate the confirmation notice.")

                raise validators.Invalid(
                    msg, 
                    field_dict["username"], 
                    state, 
                    error_dict=dict(username=msg))
            elif authval == field_dict["regval"]:
                # That's fine, just renew the conf request
                pass


class UniqueEmail(validators.FormValidator):
    """Used only in registration forms.

    Username is only a screen name, the real token that we use is
    email.  We only allow it once it the system.
    """
    validate_partial_form = True

    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        if field_dict["regtype"] == "email":
            user = model.User.query.selectfirst_by(email=field_dict["regval"])

            if user:
                if user.status != "conf_pending":
                    raise validators.Invalid(
                        "A user with this email address already exists", 
                        field_dict["regval"], 
                        state)

                if user.status == "conf_pending" \
                        and user.username != field_dict["username"]:
                    msg = ("This email address is pending confirmation."
                           "  If you submitted the first request,"
                           "  retry with the "
                           "  previous username to reactivate the"
                           "  confirmation notice.")
                    raise validators.Invalid(
                        msg, 
                        field_dict["regval"], 
                        state, 
                        error_dict=dict(regval=msg))
        # the rest is handled properly by UniqueUser


class UniqueOpenID(validators.FormValidator):
    # TODO: merge with UniqueEmail
    """Used only in registration forms.

    Username is only a screen name, the real token that we use is
    openid.  We only allow it once it the system.
    """
    validate_partial_form = True

    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        if field_dict["regtype"] == "openid":
            user = model.User.query.selectfirst_by(openid=field_dict["regval"])

            if user:
                if user.status != "conf_pending":
                    raise validators.Invalid(
                        "A user with this openid already exists", 
                        field_dict["regval"], 
                        state)

                if user.status == "conf_pending" \
                        and user.username != field_dict["username"]:
                    msg = ("This openid is pending confirmation."
                           "  If you submitted the first request,"
                           "  retry with the "
                           "  previous username to reactivate the"
                           "  confirmation notice.")
                    raise validators.Invalid(
                        msg, 
                        field_dict["regval"], 
                        state, 
                        error_dict=dict(regval=msg))
        # the rest is handled properly by UniqueUser

            
class RegisterForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    regval = validators.UnicodeString(not_empty=True)
    regtype = validators.OneOf(["email", "openid"])
    username = UsernameValidator()
    chained_validators = [AuthValidator(), 
                          UniqueUser(), 
                          UniqueEmail(), 
                          UniqueOpenID()]


class LoginOpenIDForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    openid = ActiveOpenIDValidator()


class LoginEmailForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    email = ActiveEmailValidator(not_empty=True)
    password = validators.UnicodeString(not_empty=True)
    chained_validators = [LoginEmailPasswordValidator()]


class PassResetForm(Schema):
    # TODO: check pass strenght
    allow_extra_fields = True
    filter_extra_fields = True
    password = All(validators.UnicodeString(not_empty=True), 
                   validators.MinLength(6))
    password_confirm = validators.UnicodeString(not_empty=True)
    chained_validators = [validators.FieldsMatch('password', 
                                                 'password_confirm')]


class VisitorController(BaseController):
    def login(self):
        if request.method == 'GET':
            return render('/login.mako')
        else:
            abort(403)

    
    def login_openid_form(self):
        return render("/login_openid_form.mako")

    
    @validate(schema=LoginOpenIDForm(), form='login_openid_form')
    def login_openid_action(self):
        if request.method == 'GET':
            abort(403)

        cons = openid_consumer()
        auth_request = cons.begin(self.form_result["openid"])

        # insert the pending conf request
        user = model.User.query.selectfirst_by(openid=self.form_result['openid'], 
                                         status="active")
        if not user:
            # This should not happen, it is validated in the form.
            raise "invalid request"
        
        # Compute the trust root and return URL values to build the
        # redirect information.
        return_to = h.fq_url_for(action="login_openid_conf", 
                                 controller="visitor")

        # TODO: handle the AJAX way too
        url = auth_request.redirectURL(h.site_base(), return_to)

        session.save()
        return redirect_to(url)


    def login_openid_conf(self):
        cons = openid_consumer()
        params = request.params.mixed()
        resp = cons.complete(params)

        if resp.status == consumer.SUCCESS:
            openid = normalizeURI(params['openid.identity'])
            user = model.User.query.selectfirst_by(openid=openid, status='active')
            if not user:
                # this should not happen, validation is made in the form
                raise "invalid request"

            h.q_info("You are recognized")
            h.set_auth_cookie(user.username)
            # TODO: redirect where he was
            return redirect_to("/")
                
        # all of those are failures
        c.m_warn.append("authentication failed")
        if isinstance(resp, consumer.CancelResponse):
            # those don't have messages
            c.fail_msg = "request cancelled"

        if isinstance(resp, consumer.FailureResponse):
            c.fail_msg = resp.message
        return render("/openid_failure.mako")



    def login_email_form(self):
        return render("/login_email_form.mako")


    @validate(schema=LoginEmailForm(), form='login_email_form')
    def login_email_action(self):
        if request.method == 'GET':
            abort(403)
        user = model.User.query.selectfirst_by(email=self.form_result["email"])
        if user and user.check_password(self.form_result["password"]):
            h.q_info("You are recognized")
            h.set_auth_cookie(user.username)
            # TODO: redirect where he was
            return redirect_to("/")
        else:
            # this should not happen, validated in the form
            raise "invalid request"


    def logout(self):
        h.q_info("You have been logged out")
        return redirect_to("/")

    def _add_profile_actions(self, username):
        if authorized(RemoteUser()):
            if request.environ["REMOTE_USER"] == username:
                user = model.User.query.selectfirst_by(username=username, 
                                                 status="active")

                c.nav3_actions.append(("edit profile", 
                                       "visitor", 
                                       "user_profile_edit_form"))

                c.nav3_actions.append(("messages: %d new" % len(user.new_mails),
                                       "/gazmail", 
                                       "inbox"))

                
    def user_profile(self, username):
        c.title = "%s's profile" % username
        c.username = username
        self._add_profile_actions(username)
        
        return render('/user_profile.mako')


    @authorize(RemoteUser())
    def user_profile_edit_form(self, username):
        if request.environ["REMOTE_USER"] != username:
            abort(403)
                
        c.user = model.User.query.selectfirst_by(username=username, 
                                           status="active")

        return render('/user_profile_edit_form.mako')


    @validate(schema=RegisterForm(), form='registration_form')
    def register(self):
        user = model.User.query.selectfirst_by(username=self.form_result['username'], 
                                             status="conf_pending")
        if self.form_result['regtype'] == "openid":
            # TODO: there is much in common with the login form, we
            # should factor something out

            cons = openid_consumer()
            auth_request = cons.begin(self.form_result["regval"])
            
            # insert the pending user and conf request
            user = model.User.query.selectfirst_by(username=self.form_result['username'], 
                                             status="conf_pending")
            if not user:
                user = model.User(username=self.form_result['username'], 
                                  openid=self.form_result['regval'], 
                                  authtype="openid")
            conf = model.Confirmation(user=user,
                                      authtype="openid")
            model.full_commit()

            # Compute the trust root and return URL values to build the
            # redirect information.
            return_to = h.fq_url_for(action="confirm_openid", 
                                     controller="visitor",
                                     key=conf.key, 
                                     username=user.username)

            # TODO: handle the AJAX way too
            url = auth_request.redirectURL(h.site_base(), return_to)

            session.save()
            return redirect_to(url)
        
        # Email conf
        if not user:
            user = model.User(username=self.form_result['username'], 
                              email=self.form_result['regval'], 
                              authtype="email")
        conf = model.Confirmation(user=user,
                                  authtype="email")
        model.full_commit()
        c.to_addr = self.form_result['regval']
        c.conf_url = h.fq_url_for(action="confirm_email", 
                                  controller="visitor",
                                  key=conf.key, 
                                  username=user.username)
        h.render_email("/new_reg_email.mako")

        # TODO: better message
        h.q_info("A confirmation email was sent to %s." % c.to_addr)
        # TODO: redirect to where he was
        return redirect_to("/")

    def confirm_openid(self, username, key):
        cons = openid_consumer()
        params = request.params.mixed()
        resp = cons.complete(params)

        if resp.status == consumer.SUCCESS:
            conf = model.Confirmation.query.selectfirst_by(key=key)
            # We can queue messages.  If he went that far, he has
            # cookies.
            if not conf:
                h.q_warn("inexistant or expired authentication request")
                return redirect_to("/")
            
            if conf.expiration_date < datetime.now():
                h.q_warn("expired authentication request")
                return redirect_to("/")
                
            if conf.user.username != username:
                h.q_warn("invalid authentication request")
                return redirect_to("/")

            if conf.user.status != "conf_pending":
                h.q_warn("User %s does not require account validation. "
                            "Request canceled." % conf.user.username)
                return redirect_to("/")
            
            # We are all set, everything is legit!
            conf.user.status = "active"
            # we could delete it but we just track a few stats
            conf.expireration_date = datetime.now()
            model.full_commit()

            # set the auth cookie
            h.set_auth_cookie(username)

            # TODO: make a better welcome page
            h.q_info("Welcome!")
            return redirect_to("/")
        # all of those are failures
        c.m_warn.append("authentication failed")
        if isinstance(resp, consumer.CancelResponse):
            # those don't have messages
            c.fail_msg = "request cancelled"

        if isinstance(resp, consumer.FailureResponse):
            c.fail_msg = resp.message
        return render("/openid_failure.mako")
    
    @validate(schema=PassResetForm(), form='confirm_email')
    def confirm_email_action(self, username, key):
        # TODO: this is really similar to confirm_openid(), we should
        #       merge the similarities

        conf = model.Confirmation.query.selectfirst_by(key=key)
        # We can queue messages.  If he went that far, he has
        # cookies.
        if not conf:
            h.q_warn("inexistant or expired authentication request")
            return redirect_to("/")

        if conf.expiration_date < datetime.now():
            h.q_warn("expired authentication request")
            return redirect_to("/")

        if conf.user.username != username:
            h.q_warn("invalid authentication request")
            return redirect_to("/")

        if conf.user.status != "conf_pending":
            h.q_warn("User %s does not require account validation. "
                        "Request canceled." % conf.user.username)
            return redirect_to("/")

        if request.method == 'GET':
            abort(403) 
        
        conf.user.status = "active"

        # update salt and hash
        conf.user.set_password(self.form_result['password'])

        # we could delete it but we just track a few stats
        conf.expireration_date = datetime.now()
        model.full_commit()

        # set the auth cookie
        h.set_auth_cookie(username)

        # TODO: make a better welcome page
        h.q_info("Welcome!")
        return redirect_to("/")


    def confirm_email(self, username, key):
        # TODO: this is really similar to confirm_openid(), we should
        #       merge the similarities

        # In GET, we check the conf data and show the passwd reset
        # form is all is in order.  

        # In POST, we also check the conf data and we activate the
        # user and set his pass if all is fine.

        conf = model.Confirmation.query.selectfirst_by(key=key)
        # We can queue messages.  If he went that far, he has
        # cookies.
        if not conf:
            h.q_warn("inexistant or expired authentication request")
            return redirect_to("/")

        if conf.expiration_date < datetime.now():
            h.q_warn("expired authentication request")
            return redirect_to("/")

        if conf.user.username != username:
            h.q_warn("invalid authentication request")
            return redirect_to("/")

        if conf.user.status != "conf_pending":
            h.q_warn("User %s does not require account validation. "
                        "Request canceled." % conf.user.username)
            return redirect_to("/")

        # confirmation data is fine, proceed with form or pass reset
        if request.method == 'GET':
            # routes memory does all the work
            c.form_action = h.url_for(action="confirm_email_action")
            return render('/reset_pass_form.mako')
        else:
            abort(403)

    def registration_form(self):
        return render('/registration_form.mako')
