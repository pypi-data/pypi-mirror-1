# -*- coding: utf-8 -*-

from cubicweb.selectors import implements, score_entity
from cubicweb.web.box import EntityBoxTemplate
from cubicweb.web.htmlwidgets import SideBoxWidget, BoxLink

def has_rncs(entity):
    return entity.rncs is not None

def url_societecom(entity):
    url = 'http://www.societe.com/'
    if entity.rncs:
        url += 'cgi-bin/recherche?rncs=%s' % entity.rncs
    return url

def url_score3(entity):
    url = 'http://www.score3.fr/'
    if entity.rncs:
        url += 'entreprises.shtml?chaine=%s' % entity.rncs
    elif entity.name:
        url += 'entreprises.shtml?chaine=%s' % entity.name
    return url

def url_linkedin(entity):
    url = 'http://www.linkedin.com/companies/'
    if entity.name:
        url += entity.name
    return url

def url_viadeo(entity):
    url = 'http://www.viadeo.com/'
    if entity.name:
        url += 'recherche/transverse/index.jsp?queryString=%s&search=go' % entity.name
    return url


class CompanySeeAlso(EntityBoxTemplate):
    __regid__ = 'company_seealso_box'
    __select__ = EntityBoxTemplate.__select__ & implements('Company') #& score_entity(has_rncs)
    order = 25

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        box = SideBoxWidget(self._cw._('This company on other sites'),
                            'company_sites%i' % entity.eid)
        box.append(BoxLink(url_societecom(entity), u'Société.com'))
        box.append(BoxLink(url_score3(entity), u'Score3.fr'))
        box.append(BoxLink(url_linkedin(entity), u'LinkedIn'))
        box.append(BoxLink(url_viadeo(entity), u'Viadeo'))
        self.w(box.render())
