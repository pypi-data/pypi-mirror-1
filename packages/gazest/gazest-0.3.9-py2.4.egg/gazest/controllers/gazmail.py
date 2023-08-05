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
from gazest.lib.formutil import *

from authkit.permissions import NotAuthenticatedError, NotAuthorizedError
from authkit.permissions import RemoteUser, RequestPermission
from authkit.pylons_adaptors import authorize


log = logging.getLogger(__name__)


class ComposeForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    username = ActiveUsernameValidator()
    subject = validators.UnicodeString(not_empty=True)
    body = validators.UnicodeString(not_empty=True)


class GazmailController(BaseController):
    def _add_gazmail_actions(self):
        user = h.get_remote_user()
        c.nav3_actions.append(("%d new messages" % len(user.new_mails),
                               "/gazmail", 
                               "inbox"))
        c.nav3_actions.append(("compose",
                               "/gazmail", 
                               "compose_form"))

    # TODO: refactor the mail to another controller
    @authorize(RemoteUser())
    def inbox(self):
        self._add_gazmail_actions()

        c.user = h.get_remote_user()
        return render('/gazmail_inbox.mako')

    @authorize(RemoteUser())
    def compose_form(self):
        c.form_action = h.url_for(controller='gazmail', 
                                  action='compose_form_action')
        self._add_gazmail_actions()
        return render('/gazmail_compose_form.mako')

    @authorize(RemoteUser())
    @validate(schema=ComposeForm(), form='compose_form')
    def compose_form_action(self):
        if request.method == 'GET':
            abort(403)

        from_user = h.get_remote_user()
        to_username = self.form_result["username"]
        to_user = model.User.query.selectfirst_by(username=to_username, 
                                            status="active")

        # TODO: implement draft saving
        gazmail = model.Gazmail(to_user=to_user, 
                                from_user=from_user, 
                                subject=self.form_result["subject"], 
                                body=self.form_result["body"],
                                sender_status="sent")
        model.full_commit()
        h.q_info("new message sent to %s" % to_username)
        
        return redirect_to(h.url_for(controller="/gazmail", 
                                     action="inbox"))

    def _check_can_read(self, msg_id):
        """Return the message it is can be read, abort request otherwise."""
        gazmail = model.Gazmail.query.selectfirst_by(id=int(msg_id))
        if not gazmail:
            abort(404)
        if gazmail.to_user != h.get_remote_user():
            abort(403)
        if gazmail.sender_status != "sent":
            abort(403)
        return gazmail
        


    @authorize(RemoteUser())
    def message_read(self, msg_id):
        c.gazmail = self._check_can_read(msg_id)
        c.gazmail.reader_status = "read"
        model.full_commit()
        self._add_gazmail_actions()

        c.nav3_actions.append(("reply",
                               "gazmail", 
                               "message_reply_form"))

        # we always save anyway, just go to inbox
        c.nav3_actions.append(("save",
                               "/gazmail", 
                               "inbox"))
        c.nav3_actions.append(("delete",
                               "gazmail", 
                               "message_delete"))

        if c.gazmail.is_important:
            c.nav3_actions.append(("make unimportant",
                                   "gazmail", 
                                   "message_make_unimportant"))
        else:
            c.nav3_actions.append(("make important",
                                   "gazmail", 
                                   "message_make_important"))
        
        return render('/gazmail_message_read.mako')


    @authorize(RemoteUser())
    def message_delete(self, msg_id):
        c.gazmail = self._check_can_read(msg_id)
        c.gazmail.reader_status = "deleted"
        model.full_commit()

        h.q_info("Message deleted")
        return redirect_to(h.url_for(action="inbox", controller="/gazmail"))


    @authorize(RemoteUser())
    def message_make_important(self, msg_id):
        c.gazmail = self._check_can_read(msg_id)
        c.gazmail.is_important = True
        model.full_commit()

        h.q_info("Message is now important")
        return redirect_to(h.url_for(action="message_read",
                                     controller="gazmail"))

    @authorize(RemoteUser())
    def message_make_unimportant(self, msg_id):
        c.gazmail = self._check_can_read(msg_id)
        c.gazmail.is_important = False
        model.full_commit()

        h.q_info("Message is now unimportant")
        return redirect_to(h.url_for(action="message_read",
                                     controller="gazmail"))


    @authorize(RemoteUser())
    def message_reply_form(self, msg_id):
        c.parent_gazmail = self._check_can_read(msg_id)

        c.subject = "Re: %s" % c.parent_gazmail.subject.strip("Re: ")
        c.to_username = c.parent_gazmail.to_user.username
        c.form_action = h.url_for(action="message_reply_action")

        # TODO: disable to_username

        self._add_gazmail_actions()
        return render('/gazmail_message_reply_form.mako')


    @authorize(RemoteUser())
    @validate(schema=ComposeForm(), form='message_reply_form')
    def message_reply_action(self, msg_id):
        c.parent_gazmail = self._check_can_read(msg_id)
        from_user = h.get_remote_user()

        # TODO: implement draft saving
        gazmail = model.Gazmail(to_user=c.parent_gazmail.from_user, 
                                from_user=from_user, 
                                subject=self.form_result["subject"], 
                                body=self.form_result["body"],
                                sender_status="sent")

        c.parent_gazmail.is_replied = True
        model.full_commit()
        to_username = c.parent_gazmail.from_user.username
        h.q_info("new message sent to %s" % to_username)

        return redirect_to(h.url_for(action="inbox", controller="/gazmail"))
