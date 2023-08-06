"""Specific views and actions for application using the Comment entity type

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from itertools import count

from logilab.mtconverter import xml_escape
from logilab.common.decorators import monkeypatch

from simplejson import dumps

from cubicweb.selectors import (one_line_rset, implements,
                                has_permission, relation_possible, yes,
                                match_kwargs, score_entity,
                                authenticated_user)
from cubicweb.view import EntityView
from cubicweb.uilib import rql_for_eid, cut, safe_cut
from cubicweb.mixins import TreeViewMixIn
from cubicweb.web import stdmsgs, uicfg
from cubicweb.web.action import LinkToEntityAction, Action
from cubicweb.web.form import FormViewMixIn
from cubicweb.web.formwidgets import Button
from cubicweb.web.views import primary, baseviews, xmlrss
from cubicweb.web.component import EntityVComponent
from cubicweb.web.views.basecontrollers import JSonController


uicfg.autoform_section.tag_subject_of(('*', 'comments', '*'), formtype='main', section='hidden')
uicfg.autoform_section.tag_object_of(('*', 'comments', '*'), formtype='main', section='hidden')
uicfg.actionbox_appearsin_addmenu.tag_subject_of(('*', 'comments', '*'),  False)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('*', 'comments', '*'), False)
uicfg.primaryview_section.tag_subject_of(('*', 'comments', '*'),  'hidden')
uicfg.primaryview_section.tag_object_of(('*', 'comments', '*'), 'hidden')
# XXX this is probably *very* inefficient since we'll fetch all entities created by the user
uicfg.primaryview_section.tag_object_of(('*', 'created_by', 'CWUser'), 'relations')
uicfg.primaryview_display_ctrl.tag_object_of(
    ('*', 'created_by', 'CWUser'),
    {'vid': 'list', 'label': _('latest comment(s):'), 'limit': True,
     'filter': lambda rset: rset.filtered_rset(lambda x: x.e_schema == 'Comment')})

def _login_register_link(req):
    if 'registration' in req.vreg.config.cubes():
        link = u'<a href="%s">%s</a> or ' % (req.build_url('register'),
                                             req._(u'register'))
    else:
        link = u''
    link += u'<a class="loadPopupLogin">%s</a>' % req._(u'login')
    return link

# comment views ###############################################################

class CommentPrimaryView(primary.PrimaryView):
    __select__ = implements('Comment')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.comment.css')
        entity = self.cw_rset.complete_entity(row, col)
        # display text, author and creation date
        self.w(u'<div class="comment">')
        self.w(u'<div class="commentInfo">')
        # do not try to display creator when you're not allowed to see CWUsers
        if entity.creator:
            authorlink = entity.creator.view('oneline')
            self.w(u'%s %s\n' % (self._cw._('written by'), authorlink))
        self.w(self._cw.format_date(entity.creation_date))
        # commented object
        if entity.comments:
            self.w(u",  %s " % self._cw._('comments'))
            entity.comments[0].view('oneline', w=self.w)
            self.w(u"\n")
        # don't include responses in this view, since the comment section
        # component will display them
        self.w(u'</div>\n')
        self.w(u'<div class="commentBody">%s</div>\n'
               % entity.printable_value('content'))
        # XXX attribute generated_by added by email component
        if hasattr(self, 'generated_by') and self.generated_by:
            gen = self.generated_by[0]
            link = '<a href="%s">%s</a>' % (gen.absolute_url(),
                                            gen.dc_type().lower())
            txt = self._cw._('this comment has been generated from this %s') % link
            self.w(u'<div class="commentBottom">%s</div>\n' % txt)
        self.w(u'</div>\n')



class CommentOneLineView(baseviews.OneLineView):
    __select__ = implements('Comment')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        root = entity.root()
        self.w(u'[<a href="%s">#%s</a>] '
               % (xml_escape(root.absolute_url()), root.eid))
        maxsize = self._cw.property_value('navigation.short-line-size')
        maxsize = maxsize - len(str(root.eid))
        content = entity.printable_value('content', format='text/plain')
        content = xml_escape(cut(content, maxsize))
        self.w(u'<a href="%s">#%s <i>%s</i></a>\n' % (
            xml_escape(entity.absolute_url()), entity.eid, content))


class CommentTreeItemView(baseviews.ListItemView):
    __regid__ = 'treeitem'
    __select__ = implements('Comment')

    def cell_call(self, row, col, **kwargs):
        self._cw.add_js('cubicweb.ajax.js')
        self._cw.add_css('cubes.comment.css')
        entity = self.cw_rset.get_entity(row, col)
        actions = self._cw.vreg['actions']
        self.w(u'<div class="commentInfo">')
        self.w(self._cw.format_date(entity.creation_date))
        self.w(u' %s' % self._cw.format_time(entity.creation_date))
        if entity.creator:
            authorlink = entity.creator.view('oneline')
            self.w(u', %s <span class="author">%s</span> \n'
                   % (self._cw._('written by'), authorlink,))
        replyaction = actions.select_or_none('reply_comment', self._cw,
                                       rset=self.cw_rset, row=row)
        if replyaction is not None:
            url = self._cw.build_ajax_replace_url(
                'comment%sHolder' % entity.eid, rql_for_eid(entity.eid),
                'inlinecomment')
            if self._cw.cnx.anonymous_connection:
                self.w(u' | <span class="replyto">%s <a href="%s">%s</a></span>'
                       % (_login_register_link(self._cw),
                          xml_escape(url), self._cw._(replyaction.title)))
            else:
                self.w(u' | <span class="replyto"><a href="%s">%s</a></span>'
                       % (xml_escape(url), self._cw._(replyaction.title)))
        editaction = actions.select_or_none('edit_comment', self._cw,
                                            rset=self.cw_rset, row=row)
        if editaction is not None:
            url = self._cw.build_ajax_replace_url(
                'comment%s' % entity.eid, rql_for_eid(entity.eid),
                'editcomment')
            self.w(u' | <span class="replyto"><a href="%s">%s</a></span>'
                   % (xml_escape(url), self._cw._(editaction.title)))

        deleteaction = actions.select_or_none('delete_comment', self._cw,
                                             rset=self.cw_rset, row=row)
        if deleteaction is not None:
            url = self._cw.build_ajax_replace_url(
                'comment%s' % entity.eid, rql_for_eid(entity.eid),
                'deleteconf')
            self.w(u' | <span class="replyto"><a href="%s">%s</a></span>'
                   % (xml_escape(url), self._cw._(deleteaction.title)))

        self.w(u'</div>\n')
        text = entity.printable_value('content')
        if not kwargs.get('full'):
            maxsize = self._cw.property_value('navigation.short-line-size')
            text = safe_cut(text, maxsize)
        self.w(u'<div class="commentBody">%s</div>\n' % text)
        self.w(u'<div id="comment%sHolder"></div>' % entity.eid)


class CommentThreadView(TreeViewMixIn, baseviews.ListView):
    """a recursive tree view"""
    __select__ = implements('Comment')
    title = _('thread view')

    def open_item(self, entity):
        self.w(u'<li id="comment%s" class="comment">\n' % entity.eid)


# comment edition views #######################################################

class InlineCommentView(EntityView):
    __regid__ = 'inlinecomment'
    __select__ = yes() # explicit call when it makes sense

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.wview('inlinecommentform', None, commented=entity)


class InlineEditCommentForm(FormViewMixIn, EntityView):
    __regid__ = 'editcomment'
    __select__ = implements('Comment')

    jsfunc = "processComment(%s, '%s')"
    jsonmeth = 'edit_comment'

    def cell_call(self, row, col):
        self.comment_form(self.cw_rset.get_entity(row, col))

    def comment_form(self, commented, newcomment=None):
        self._cw.add_js('cubes.comment.js')
        if newcomment is None:
            newcomment = commented
        # hack to avoid tabindex conflicts caused by Ajax requests
        self._cw.next_tabindex = count(20).next
        jseid = dumps(commented.eid)
        buttons = [Button(onclick=self.jsfunc % (jseid, self.jsonmeth)),
                   Button(stdmsgs.BUTTON_CANCEL,
                          onclick=self.jsfunc % (jseid, ''))]
        form = self._cw.vreg['forms'].select('edition', self._cw,
                                             entity=newcomment,
                                             form_buttons=buttons)
        self.w(u'<div id="comment%sSlot">%s</div>' % (
            commented.eid, form.render(main_form_title=u'',
                                       display_label=False,
                                       display_relations_form=False)))


class InlineCommentForm(InlineEditCommentForm):
    __regid__ = 'inlinecommentform'
    __select__ = match_kwargs('commented') # explicit call when it makes sense

    jsonmeth = 'add_comment'

    def call(self, commented):
        newcomment = self._cw.vreg['etypes'].etype_class('Comment')(self._cw)
        newcomment.eid = self._cw.varmaker.next()
        self.comment_form(commented, newcomment)


# comment component ###########################################################

class CommentSectionVComponent(EntityVComponent):
    """a component to display a <div> html section including comments
    related to an object
    """
    __regid__ = 'commentsection'
    __select__ = (EntityVComponent.__select__
                  & relation_possible('comments', 'object', 'Comment'))

    context = 'navcontentbottom'

    def cell_call(self, row, col, view=None):
        req = self._cw
        req.add_js( ('cubicweb.ajax.js', 'cubes.comment.js') )
        eid = self.cw_rset[row][col]
        self.w(u'<div id="%s" class="%s" cubicweb:rooteid="%s">' % (
            self.div_id(), self.div_class(), eid))
        rql = u'Any C,CD,CC,CCF,U,UL,US,UF ORDERBY CD WHERE C is Comment, '\
              'C comments X, C creation_date CD, C content CC, C content_format CCF, ' \
              'C created_by U?, U login UL, U firstname UF, U surname US, X eid %(x)s'
        rset = req.execute(rql, {'x': eid}, 'x')
        if rset.rowcount:
            self.w(u'<h4>%s</h4>' % (req._('Comment_plural')))
        addcomment = self._cw.vreg['actions'].select_or_none('reply_comment', req,
                                                        rset=self.cw_rset,
                                                        row=row, col=col)
        if addcomment is not None:
            url = req.build_ajax_replace_url(
                'comment%sHolder' % eid, rql_for_eid(eid), 'inlinecomment')
            self.w(u' (<a href="%s" onclick="javascript:toggleVisibility(\'addCommentLinks\');">%s</a>)' % (url, req._(addcomment.title)))
            # XXX still necessary?
            #if req.use_fckeditor() and req.property_value('ui.default-text-format') == 'text/html':
            #    req.fckeditor_config()
        if req.cnx.anonymous_connection:
            self.w(u'<div id="addCommentLinks" class="hidden">%s %s</div>' % \
                   (_login_register_link(req), req._(u'to comment')))
        self.w(u'<div id="comment%sHolder"></div>' % eid)
        if rset.rowcount:
            self.w(u'<ul class="comment">')
            for i in xrange(rset.rowcount):
                self.wview('tree', rset, row=i, full=True)
            self.w(u'</ul>')
        self.w(u'</div>')


# comment actions #############################################################

class ReplyCommentAction(LinkToEntityAction):
    __regid__ = 'reply_comment'
    __select__ = LinkToEntityAction.__select__ & implements('Comment')

    rtype = 'comments'
    role = 'object'
    target_etype = 'Comment'

    title = _('reply to this comment')
    category = 'hidden'
    order = 111

    def url(self):
        comment = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        linkto = '%s:%s:subject' % (self.rtype, comment.eid)
        return self._cw.build_url(vid='creation', etype=self.target_etype,
                                  __linkto=linkto,
                                  __redirectpath=comment.root().rest_path(),
                                  __redirectvid=self._cw.form.get('vid', ''))


class AddCommentAction(LinkToEntityAction):
    """add comment is like reply for everything but Comment"""
    __regid__ = 'reply_comment'
    __select__ = LinkToEntityAction.__select__ & ~implements('Comment')

    rtype = 'comments'
    role = 'object'
    target_etype = 'Comment'

    title = _('add comment')
    category = 'hidden'
    order = 111


class EditCommentAction(Action):
    __regid__ = 'edit_comment'
    __select__ = one_line_rset() & implements('Comment') & has_permission('update')

    title = _('edit comment')
    category = 'hidden'
    order = 110

    def url(self):
        return self._cw.build_url(rql=self.cw_rset.printable_rql(), vid='edition')

class DeleteCommentAction(Action):
    __regid__ = 'delete_comment'
    __select__ = implements('Comment') & \
                 authenticated_user() & \
                 score_entity(lambda x: not x.reverse_comments and x.has_perm('delete'))

    title = _('delete comment')
    category = 'hidden'
    order = 110

    def url(self):
        return self._cw.build_url(rql=self.cw_rset.printable_rql(), vid='deleteconf')

# add some comments related methods to the Jsoncontroller #####################

@monkeypatch(JSonController)
def js_add_comment(self, commented, text, format):
    self._cw.execute('INSERT Comment C: C comments X, C content %(text)s, '
                     'C content_format %(format)s  WHERE X eid %(x)s',
                     {'format' : format, 'text' : text, 'x' : commented}, 'x')

@monkeypatch(JSonController)
def js_edit_comment(self, comment, text, format):
    self._cw.execute('SET C content %(text)s, C content_format %(format)s '
                     'WHERE C eid %(x)s',
                     {'format' : format, 'text' : text, 'x' : comment}, 'x')


# RSS view ####################################################################

class RssItemCommentView(xmlrss.RSSItemView):
    __select__ = implements('Comment')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<item>\n')
        self.w(u'<guid isPermaLink="true">%s</guid>\n'
               % xml_escape(entity.absolute_url()))
        self.render_title_link(entity)
        description = entity.dc_description(format='text/html') + \
                      self._cw._(u'about') + \
                      u' <a href=%s>%s</a>' % (entity.root().absolute_url(),
                                               entity.root().dc_title())
        self._marker('description', description)
        self._marker('dc:date', entity.dc_date(self.date_format))
        self.render_entity_creator(entity)
        self.w(u'</item>\n')
        self.wview('rssitem', entity.related('comments', 'object'), 'null')
