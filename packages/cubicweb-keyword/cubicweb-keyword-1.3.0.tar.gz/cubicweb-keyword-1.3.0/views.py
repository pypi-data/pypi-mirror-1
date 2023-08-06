"""Specific views for keywords / classification schemes

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import simplejson

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import html_escape

from cubicweb.selectors import implements, rql_condition, relation_possible
from cubicweb.view import EntityView
from cubicweb.common.mixins import TreePathMixIn
from cubicweb.web import stdmsgs, uicfg, component
from cubicweb.web.views import primary, baseviews, basecontrollers

# displayed by the above component
uicfg.primaryview_section.tag_object_of(('*', 'applied_to', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('*', 'applied_to', '*'), 'hidden')

uicfg.actionbox_appearsin_addmenu.tag_object_of(('Keyword', 'included_in', 'Classification'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Keyword', 'subkeyword_of', 'Keyword'), True)
uicfg.autoform_section.tag_object_of(('Keyword', 'in_state', '*'), 'generated')

# keyword views ###############################################################

class KeywordPrimaryView(primary.PrimaryView):
    __select__ = implements('Keyword')

    def cell_call(self, row, col, **kwargs):
        entity = self.entity(row, col)
        self.w(u'<h1 class="titleUnderline">%s [%s]</h1>' % (
            html_escape(entity.name), html_escape(entity.state)))
        rset = entity.related('applied_to')
        if rset:
            self.wview('list', rset)
        else:
            self.w(self.req._('no tagged object'))


class KeywordOneLineView(baseviews.InContextView):
    __select__ = implements('Keyword')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        if entity.state == 'validation pending':
            cssclass = u'class="needsvalidation"'
        else:
            cssclass = u''
        self.w(u'<a href="%s" %s>%s</a>' % (html_escape(entity.absolute_url()),
                                            cssclass,
                                            html_escape(entity.name)))


class KeywordComboBoxView(TreePathMixIn, EntityView):
    """display keyword in edition's combobox"""
    __select__ = implements('Keyword', 'Classification')
    id = 'combobox'
    item_vid = 'text'
    separator = u' > '


# keyword component ###########################################################

class KeywordBarVComponent(component.EntityVComponent):
    """the keywords path bar: display keywords of a tagged entity"""
    id = 'keywordsbar'
    __select__ = component.EntityVComponent.__select__ & \
                 relation_possible('applied_to', 'object', 'Keyword')
    context = 'header'
    order = 152
    htmlclass = 'navigation'

    def call(self, **kwargs):
        entity = self.entity(0)
        # managers can see all applied keyword, other users will only see validated
        # keywords or their own ones
        if self.req.user.is_in_group('managers'):
            rset = entity.related('applied_to', 'object')
        else:
            rset = self.cursor.execute('DISTINCT Any K,N WHERE K name N, K applied_to X, X eid %(x)s, '
                                       '(K owned_by U, U eid %(u)s) or (K in_state ST, ST name "keyword validated")',
                                       {'x' : entity.eid, 'u' : self.req.user.eid}, 'x')
        if rset:
            self.w(u'<div class="%s" id="%s">\n' % (self.div_class(), self.div_id()))
            self.w(u'<span>%s</span>&nbsp;' % self.req._('keywords:'))
            self.wview('csv', rset, 'null', done=set())
            self.w(u'</div>\n')
        else:
            self.w(u'<div class="%s hidden" id="%s"></div>\n' % (
                self.div_class(), self.div_id()))


class AddKeywordVComponent(component.EntityVComponent):
    """the 'add keyword' component"""
    id = 'addkeywords'
    __select__ = component.EntityVComponent.__select__ & \
                 relation_possible('applied_to', 'object', 'Keyword', action='add') & \
                 rql_condition('X is ET, CL classifies ET')

    context = 'header'
    order = 153
    htmlclass = 'navigation'

    def call(self):
        self.add_js(['cubicweb.widgets.js', 'cubes.keyword.js'])
        self.req.add_css('cubicweb.suggest.css')
        entity = self.entity(0)
        self.w(u'<table><tr><td>')
        self.w(u'<a class="button sglink" href="javascript: showKeywordSelector(%s, \'%s\', \'%s\');">%s</a></td>' % (
            entity.eid, self.req._(stdmsgs.BUTTON_OK),
            self.req._(stdmsgs.BUTTON_CANCEL), self.req._('add keywords')))
        self.w(u'<td><div id="kwformholder"></div>')
        self.w(u'</td></tr></table>')

# add some classification schema related methods to the Jsoncontroller ########

@monkeypatch(basecontrollers.JSonController)
@basecontrollers.jsonize
def js_possible_keywords(self, eid):
    rql = ('DISTINCT Any N WHERE K is Keyword, K name N, NOT K applied_to X, '
           'X eid %(x)s, K included_in C, C classifies ET, X is ET')
    rset = self.cursor.execute(rql, {'x' : eid, 'u' : self.req.user.eid}, 'x')
    return [name for (name,) in rset]

@monkeypatch(basecontrollers.JSonController)
@basecontrollers.jsonize
def js_add_keywords(self, eid, kwlist):
    msg = self.req._('keywords applied')
    kwrset = self.cursor.execute('Any K,N,C WHERE K is Keyword, K name N, K included_in C, '
                                 'C classifies ET, X eid %(x)s, X is ET',
                                 {'x' : eid}, 'x')
    if not kwrset:
        return self.req._('No suitable classification scheme found')
    classification = kwrset[0][2] # XXX what if we have several classifications ?
    valid_keywords = set(kwname for _, kwname,_ in kwrset)
    user_keywords = set(kwlist)
    invalid_keywords = sorted(user_keywords - valid_keywords)
    kweids = dict( (kwname, str(kweid)) for kweid, kwname, _ in kwrset if kwname in user_keywords )
    if invalid_keywords:
        for keyword in invalid_keywords:
            neweid = self.cursor.execute('INSERT Keyword K: K name %(name)s, K included_in C WHERE C eid %(c)s',
                                         {'name' : keyword, 'c' : classification}, 'c')[0][0]
            kweids[keyword] = str(neweid)
        if not self.req.user.is_in_group('managers'):
            msg += self.req._(' but keywords %s must be validated') % u', '.join(invalid_keywords)
    if kweids:
        self.cursor.execute('SET KW applied_to X WHERE X eid %%(x)s, KW eid IN (%s)'
                            % ','.join(kweids.values()), {'x' : eid}, 'x')
    return msg
