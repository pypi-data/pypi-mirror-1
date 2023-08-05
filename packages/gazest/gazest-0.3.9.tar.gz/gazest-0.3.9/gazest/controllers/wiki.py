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
from gazest.lib import markup
from gazest.lib.wiki_util import *
from gazest.lib.formutil import IntListValidator
from gazest.lib import dag
from tempfile import NamedTemporaryFile
from datetime import datetime

import formencode
import os

log = logging.getLogger(__name__)
MERGE_CMD = ("diff3 -m -L 'your version' %s"
             " -L original %s"
             " -L 'concurrent version' %s")

CONFLICT_MSG = ("Some conflict were detected and you'll"
                " have to merge them manually.  Good luck!")

MARKERS = [ "<<<<<<<", "|||||||", "=======", ">>>>>>>" ]

class WikiPageForm(formencode.Schema):
    allow_extra_fields = True
    parent_ids = IntListValidator()
    body = formencode.validators.UnicodeString()
    comment = formencode.validators.UnicodeString(strip=True)


class AbuseReportForm(formencode.Schema):
    allow_extra_fields = True
    comment = formencode.validators.OneOf(model.ABUSE_TYPES)
    comment = formencode.validators.UnicodeString(strip=True)


def merge_revs(a, b):
    """ 3-way merge with GNU diff3 """
    lca = dag.get_lca(a, b)

    temps = []
    for rev in a, lca, b:
        temps.append(NamedTemporaryFile())
        temps[-1].write(rev.body.encode("utf-8"))
        temps[-1].file.flush()

    names = tuple([f.name for f in temps])
    pipe = os.popen(MERGE_CMD % names)
    merge = unicode(pipe.read(), "utf-8")
    error = pipe.close()
    if error == 127:
        raise Exception("diff3 is not installed")
    return error, merge


def has_conflict(body):
    for mrk in MARKERS:
        if body.find(mrk) != -1:
            return True
    return False



def get_rev(slug, for_edit=False):
    # if there is no such page, we check the namespace and return the
    # relevant not_found_rev
    page = model.Page.query.selectfirst_by(slug=slug)
    if page:
        rev = page.rev
    else:
        ns_slug = get_namespace(slug)
        namespace = model.Namespace.query.selectfirst_by(slug=ns_slug)

        if not namespace:
            log.info("no page found for '%s'" % slug)
            abort(404)

        if for_edit:
            rev = namespace.stub_rev
        else:
            rev= namespace.not_found_rev
    return page, rev
    


class WikiController(BaseController):
    def __before__(self):
        actions = [("Page", "wiki", "view"),
                   ("Edit", "wiki", "edit_form"),
                   ("History", "wiki", "diff_form")]
        c.nav3_actions += actions

            
    def _get_method_args(self):
        args = BaseController._get_method_args(self)
        if args.has_key("slug"):
            args["slug"] = normalize_slug(args["slug"])
        return args
    

    def index(self):
        slug = config["wiki_index"]

        # cheat routes so the nav links will be OK
        c.routes_dict["slug"] = slug
        
        return self.view(slug)


    def about(self):
        slug = config["wiki_about"]

        # cheat routes so the nav links will be OK
        c.routes_dict["slug"] = slug
        
        return self.view(slug)


    def random_page(self):
        # This could be O(n) depending on the DB engine
        slug_col = model.RevNode.c.slug
        page = model.RevNode.query.selectfirst(slug_col != "",
                                         order_by=model.func.random())

        # cheat routes so the nav links will be OK
        c.routes_dict["slug"] = page.slug
        
        return self.view(page.slug)


    def view(self, slug):
        page, rev = get_rev(slug)
        delay = config["wiki_indexing_delay"]
        if rev.creat_date + delay > datetime.utcnow():
            c.noindex = True
            
        page, c.body = markup.render_page(rev.body, slug)
        c.title = page.title
        return render("/wiki_view.mako")


    def edit_form(self, slug):
        # pre-fill
        page, rev = get_rev(slug, True)
        c.body = rev.body
        if page:
            c.parent_ids = [rev.id]
        else:
            c.comment = "Page creation"
        return render("/wiki_edit_form.mako")


    @validate(schema=WikiPageForm(), form='edit_form')
    def edit_action(self, slug):
        # There are essentially 3 cases of non-trivial edit:
        #  1) undo
        #  2) concurrent edit without conflict
        #  3) concurrent edit with conflicts

        # In the following text, an "edit rev" is a rev that haven't
        # been saved to database.  It might be an Alchemy object or
        # just the data to create one living in the fields of a HTML
        # form.  You need to view the edit rev as a regular DAG node
        # for the following text to make sense.

        # An edit has 0, 1, or 2 parent revs: 0 for new pages, 1 for
        # simple edits and 2 for merge and undo that are not on the
        # tip.  If we implement octopus merge, like in Git, then a
        # merge could have more than 2 parents but it's all
        # essentially the same. 

        # 1) Undo: undo of the tip just reverts to the previous tip.
        # We still add a new node with the old content: this prevent
        # cycles and allow a commit message telling why the revert has
        # been done.  The interesting case is undo deeper in the DAG.
        # We create an edit rev with content of the previous tip and
        # make it child of the rev to undo.  We then merge this edit
        # rev with the current tip with 3 way merge and fall back to
        # 2) or 3) depending on the presence of conflicts.  The edit
        # rev has 2 parents before we fall back: the rev to undo and
        # the current tip.

        # Concurrent edits, common case: each edit rev spawns from a
        # tip.  If the tip has changed (the current tip is not a
        # parent of the edit rev), we do a 3-way diff of the edit rev
        # against the new tip and this lead us to 2) or 3).
        
        # 2) Concurrent edit without conflicts: we know we have merged
        # the concurrent edit so we don't merge again as long as the
        # current tip is one of our parents.  The user can re-edit
        # several time before a final save so it's important not to
        # re-merge or there will be conflicts.  There is also the
        # possibility that the user reached this point because he
        # resolved conflicts; this is just another reason not to try to
        # remerge, we assume at this point that the user has the
        # best possible merge.  But, shit can happen if the current
        # tip change, in other words, if someone else makes a
        # concurrent edit.  No stress!  We do a 3-way merge of the
        # edit rev against the new tip AND we replace the previous tip
        # in our parent list with the new tip.  If the merge has
        # conflicts, go to 3), otherwise, stay in 2) until the user
        # saves.
        #
        # Why can we just replace one parent and be done with it?  The
        # last 3-way merge will invariably find for common parent the
        # old tip.  That means that we just merged exactly the diff
        # between the old tip and the new one.

        # 3) Concurrent edit with conflicts: this is really bad and it
        # might induce panic for the user.  We detect conflicts by the
        # presence of conflict markers.  We just stay in state 3) and
        # keep on editing until there are no conflict markers.  We
        # don't check for new tip and we don't merge because there is
        # nothing sensible to do until the markers are gone.  When the
        # markers are gone, we go to state 2).

        # That's it!  Ok there is a minor detail: user can't save if
        # there are conflicts or if the current tip is not a parent of
        # the edit rev.

        # WARNING: there should be diagrams to explain all the cases
        # and why they work.  Make sure you understood the whole thing
        # before you edit this code because if you mess the DAG, it
        # might be impossible to recover.  It's the only tricky part
        # of the whole wiki; don't break it.
        
        # flashed on this page, when preview, or on the next, when save
        # TODO: flash them
        c.title = "Editing %s" % slug
        msgs = []
        conflict = has_conflict(self.form_result["body"])

        # TODO: some slug normalization might be called for
        page = model.Page.query.selectfirst_by(slug=slug)
        rev = model.RevNode(body=self.form_result["body"],
                            comment=self.form_result["comment"],
                            slug=slug,
                            user=h.get_remote_user())

        if not page:
            # New page
            ns_slug = get_namespace(slug)
            ns = model.Namespace.query.selectfirst_by(slug=ns_slug)
            page = model.Page(slug=slug, namespace=ns)

        # this is the tip
        pre_rev = page.rev


        c.parent_ids = self.form_result["parent_ids"]
        for rev_id in c.parent_ids:
            rev.add_parent(model.RevNode.query.get(rev_id))

        if not c.parent_ids:
            # new page: nothing to merge, the rev is the new DAG root
            
            if pre_rev:
                # The page was created concurently.  We can't merge
                # but we plug the other rev in the DAG so the old
                # content isn't lost.

                log.debug("concurent creation of %s" % slug)
                rev.add_parent(pre_rev)
                # TODO: add a few links
                msgs.append("This page was created by someone else while "
                            "you were editing.  Your version takes "
                            "precedence but you can acces the other version "
                            "from this history tab.")
        elif conflict:
            # case 3: handles just before the save
            pass
        else:
            # case 2: so far so good

            # Easy case: no concurent edit and nothing to merge.
            if pre_rev.id in c.parent_ids:
                # still agaist the tip, keep editing
                pass
                
            # Harder: we need to merge
            else:
                conflict, merge = merge_revs(rev, pre_rev)
                
                msgs.append("Someone modified this page while you"
                            " were editing.")
                if not conflict:
                    msgs.append("The changes were merged without"
                                " conflicts but keep an eye open for possible"
                                " errors.")
                rev.body = merge
                c.body = merge

                # swap the tip in the parent list
                if len(c.parent_ids) > 1:
                    rev.del_parent(rev.parents()[-1])
                rev.add_parent(pre_rev)
                c.parent_ids = [r.id for r in rev.parents()]
                

        # TODO: now would be a good time to flash parse errors if any
        page.rev = rev
        
        # save if save button
        if conflict:
            # Oh shit!  Don't save: force preview.
            
            h.m_warn(CONFLICT_MSG)
            c.body = rev.body
            c.comment = rev.comment
            c.m_warn += msgs
            
            # TODO: This presentation seriously sucks.  There is no
            # way a normal human can resolve a conflict from that.  We
            # need something more like kdiff3 on the web.
            return render("/wiki_edit_form.mako")
        
        elif self.form_result.has_key("save"):
            model.full_commit()
            map(h.q_info, msgs)
            return h.redirect_to(action="view")
        # preview
        elif self.form_result.has_key("preview"):
            c.m_info.append("This is only a preview; "
                            "don't forget to save.")
            page, c.preview = markup.render_page(rev.body, slug)
            c.title = "Edit preview"
            c.body = rev.body
            c.comment = rev.comment
            c.m_info += msgs
            
            return render("/wiki_edit_form.mako")
        else:
            raise ValueError("No action specified.")


    def diff_form(self, slug):
        c.noindex = True
        page, rev = get_rev(slug)
        #c.rows = dag.html_layout(dag.FakeRev(dag.ex1, dag.ex1_h))
        c.rows = dag.html_layout(rev)
        return render("/wiki_diff_form.mako")


    def revision_diff(self, slug, to_id, from_id):
        c.noindex = True
        c.title = "Revision diff"

        # TODO: If we implement ACLs, check that the rev is accessible
        # from the page slug.

        # Plain 2-way diff.  The output might be a bit more meaningful
        # with 3-way diff but, when no merge is involved, git and
        # Mercurial are happy with 2-way diff, so shall we.
        
        to_rev = model.RevNode.query.get(to_id)
        
        if from_id:
            from_rev = model.RevNode.query.get(from_id)
        else:
            # We can have more than one parent; the default is the
            # previous page head, the last parent.
            from_rev = to_rev.parents()[-1]

        c.from_rev = from_rev
        c.to_rev = to_rev
        return render("/wiki_revision_diff.mako")


    def past_revision(self, slug, rev_id):
        c.noindex = True
        
        # TODO: if we implement ACLs, it will be important to check
        # that the rev is indeed in the page DAG.
        c.m_info.append("This is a past revision; "
                        "it might differ from the current page.")
        rev = model.RevNode.query.get(rev_id)
        page, c.body = markup.render_page(rev.body, slug)
        c.title = page.title
        return render("/wiki_view.mako")
    

    def recent_changes(self):
        c.noindex = True
        c.title = "Recent changes"
        
        # TODO: our need to do that might indicate that this action
        # belongs somewhere else
        c.nav3_actions = []
        
        slug_col = model.RevNode.c.slug
        date_col = model.desc(model.RevNode.c.creat_date)
        # TODO: paging
        c.revs = model.RevNode.query.select(slug_col!="",
                                            order_by = date_col,
                                            limit=50)        
        # Moin style of grouping
        def group(elems, key_funct):
            """ Return a list of [key, elems] pairs """
            groups = {}
            # key order is important
            keys = []
            last_elem = None
            for elem in elems:
                key = key_funct(elem)
                if not groups.has_key(key):
                    keys.append(key)
                    groups[key] = []
                groups[key].append(elem)
            return [[key, groups[key]] for key in keys]

        c.groups = [(date, group(revs, lambda r:r.slug))
                    for date, revs in group(c.revs,
                                            lambda r:r.creat_date.date())]
        
        return render("/wiki_recent_changes.mako")


    def undo_revision(self, slug, rev_id):
        c.noindex = True
        
        # TODO: if we implement ACLs, it will be important to check
        # that the rev is indeed in the page DAG.

        # Note: undo of a merge reverts to the former tip, that is,
        # the rev that had the Page pointer.  This is always
        # rev.parents()[-1]

        page = model.Page.query.selectfirst_by(slug=slug)
        badrev = model.RevNode.query.get(rev_id)
        oldtip = badrev.parents()[-1]
        conflict = False

        # TODO: we can do better than that
        c.comment = "Revert"

        editrev = model.RevNode(body=oldtip.body,
                                comment=c.comment,
                                user=h.get_remote_user())
        editrev.add_parent(badrev)
        
        if page.rev.id == badrev.id:
            # just call the old tip back: nothing to do
            pass
        else:
            # 3-way merge with curent tip
            conflict, merge = merge_revs(editrev, page.rev)
            editrev.add_parent(page.rev)
            editrev.body = merge

            if conflict:
                h.m_warn(CONFLICT_MSG)

        c.show_diff_highlight = not conflict
        
        # add a few instruction
        # TODO: this should not be a m_info but instructions on the
        # page template
        h.m_info("You are about to undo an edit."
                 " Please review the changes before you save.")
        
        # show edit form
        c.parent_ids = [r.id for r in editrev.parents()]
        c.body = editrev.body
        c.editrev = editrev
        c.page = page
        return render("/wiki_edit_form.mako")


    def page_atom(self, slug):
        c.page = model.Page.query.selectfirst_by(slug=slug)

        # Note: The feed won't show all the revs, only the ones
        # against the tip.
        slug_col = model.RevNode.c.slug
        date_col = model.desc(model.RevNode.c.creat_date)
        c.revs = model.RevNode.query.select(slug_col==slug,
                                      order_by=date_col,
                                      limit=50)

        ctype = 'application/atom+xml; charset=utf-8'
        response.headers['Content-Type'] = ctype
        return render("/wiki_page_atom.mako")


    def site_atom(self):
        slug_col = model.RevNode.c.slug
        date_col = model.desc(model.RevNode.c.creat_date)
        # TODO: paging
        c.revs = model.RevNode.query.select(slug_col!="",
                                      order_by = date_col,
                                      limit=50)

        ctype = 'application/atom+xml; charset=utf-8'
        response.headers['Content-Type'] = ctype
        return render("/wiki_site_atom.mako")


    def abuse_report_form(self, slug, rev_id):
        c.rev = model.RevNode.get(rev_id)
        return render("/wiki_abuse_report_form.mako")


    @validate(schema=AbuseReportForm(), form='abuse_report_form')
    def abuse_report_action(self, slug, rev_id):
        rev = model.RevNode.get(rev_id)
        report = model.AbuseReport(rev=rev,
                                   reporter=h.get_remote_user(),
                                   comment=self.form_result["comment"],
                                   problem=self.form_result["problem"])
        
        model.full_commit()
        h.q_info("Thank you for brining this to our attention."
                 " We'll review your report and take due actions shortly."
                 " In the mean time, feel free to undo offensive edits by"
                 " yourself.")
        
        return h.redirect_to(action="view")


