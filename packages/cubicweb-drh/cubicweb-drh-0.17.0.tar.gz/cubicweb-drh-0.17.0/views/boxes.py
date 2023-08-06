# -*- coding: utf-8 -*-

from cubicweb.web.box import BoxTemplate
from cubicweb.web.htmlwidgets import BoxWidget, BoxLink

from logilab.mtconverter import xml_escape
from cubicweb.web.box import EntityBoxTemplate

from cubicweb.selectors import implements, rql_condition
from cubicweb.web.htmlwidgets import SideBoxWidget, BoxLink

class StartupViewsBox(BoxTemplate):
    """display a box containing links to all startup views"""
    __regid__ = 'drh_workflow_box'
    visible = True # disabled by default
    title = _('State')
    order = 70

    def call(self, **kwargs):
        box = BoxWidget(self._cw._(self.title), self.__regid__)
        rset = self._cw.execute('Any S,SN,count(A) GROUPBY S,SN ORDERBY SN '
                                'WHERE A is Application, A in_state S, S name SN')
        for eid, state, count in rset:
            rql_syn = ('Any A,P,group_concat(TN),E,B '
                       'GROUPBY A,P,E,B,CD ORDERBY CD '
                       'WHERE A in_state X, X eid %s, '
                       'A for_person P, P is Person, '
                       'T? tags A, T name TN, P has_studied_in E?, '
                       'P birthday B?, A creation_date CD')
            url = self._cw.build_url(rql=rql_syn % eid,
                                 vtitle=self._cw._(state))
            label = u'%s: %s' % (state, count)
            box.append(BoxLink(url, label))

        if not box.is_empty():
            box.render(self.w)


class AttachmentsDownloadBox(EntityBoxTemplate):
    """
    A box containing all downloadable attachments concerned by Person.
    """
    __regid__ = 'concerned_by_box'
    __select__ = EntityBoxTemplate.__select__ & implements('Person')
    rtype = 'concerned_by'
    target = 'subject'
    order = 0

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        req = self._cw
        self.w(u'<div class="sideBox">')
        title = req._('concerned_by')
        self.w(u'<div class="sideBoxTitle downloadBoxTitle"><span>%s</span></div>'
            % xml_escape(title))
        self.w(u'<div class="sideBox downloadBox"><div class="sideBoxBody">')
        for attachment in entity.concerned_by:
            self.w(u'<div><a href="%s"><img src="%s" alt="%s"/> %s</a>'
                   % (xml_escape(attachment.download_url()),
                      req.external_resource('DOWNLOAD_ICON'),
                      _('download icon'), xml_escape(attachment.dc_title())))
            self.w(u'</div>')
        self.w(u'</div>\n</div>\n</div>\n')


class PeopleBox(EntityBoxTemplate):
    __regid__ = '123people_box'
    __select__ = EntityBoxTemplate.__select__ & implements('Person')
    order = 25

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        firstname = entity.firstname
        surname = entity.surname
        box = SideBoxWidget(self._cw._('The url\'s Person on 123people '),
                            'person_on_123people')
        box.append(BoxLink('http://www.123people.com/s/%s+%s/world' % (firstname, surname),
                           xml_escape('%s %s' % (firstname, surname))))
        self.w(box.render())
