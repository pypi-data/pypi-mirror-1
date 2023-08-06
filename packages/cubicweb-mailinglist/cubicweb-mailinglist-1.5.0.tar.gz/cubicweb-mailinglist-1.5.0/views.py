"""Specific views for mailinglists entities

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from cubicweb.selectors import implements, rql_condition
from cubicweb.view import EntityView
from cubicweb import tags
from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, baseviews


for attr in ('name', 'homepage', 'archive', 'mlid'):
    uicfg.primaryview_section.tag_attribute(('MailingList', attr), 'hidden')
uicfg.primaryview_section.tag_subject_of(('MailingList', 'mailinglist_of', '*'),
                                         'sideboxes')

class MLPrimaryView(primary.PrimaryView):
    __select__ = implements('MailingList')
    show_attr_label = False

    def render_entity_attributes(self, entity):
        super(MLPrimaryView, self).render_entity_attributes(entity)
        _ = self._cw._
        self.w(u'<ul>')
        if entity.homepage:
            self.w(u'<li>%s</li>' % tags.a(_('(un)subscribe'),
                                           href=entity.homepage))
        if entity.archive:
            self.w(u'<li>%s</li>' % tags.a(_('browse archives'),
                                           href=entity.archive))
        self.w(u'<li>')
        for email in entity.use_email:
            self.w(u'%s :' % _('to post on the mailinglist'))
            email.view('mailto', w=self.w)
        self.w(u'</li>')
        self.w(u'</ul>')


class MailingListDoapItemView(EntityView):
    __regid__ = 'doapitem'
    __select__ = implements('MailingList')

    def cell_call(self, row, col):
        """ element as an item for an doap description """
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<doap:mailing-list rdf:resource="%s" />\n' % entity.absolute_url())


class MLArchiveAction(action.Action):
    __regid__ = 'mlarchive'
    __select__ = implements('MailingList') & rql_condition('NOT X archive NULL')

    category = 'mainactions'
    title = _('browse archives')
    order = 20

    def url(self):
        return self.cw_rset.get_entity(0, 0).archive


class MLRegisterAction(action.Action):
    __regid__ = 'mlregister'
    __select__ = implements('MailingList') & rql_condition('NOT X homepage NULL')

    category = 'mainactions'
    title = _('(un)subscribe')
    order = 21

    def url(self):
        return self.cw_rset.get_entity(0, 0).homepage




