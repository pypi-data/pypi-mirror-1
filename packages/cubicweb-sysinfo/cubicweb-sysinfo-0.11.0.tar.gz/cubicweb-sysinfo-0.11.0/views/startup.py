"""sysinfo specific startup views

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from cubicweb.web.views import startup

class IndexView(startup.ManageView):
    __regid__ = 'index'

    def call(self):
        self.display_actions()
        self.display_services()


    def display_actions(self):
        _ = self._cw._
        w = self.w
        w(u'<table class="xxx"><tr>')
        w(u'<td><a href="/services">%s</a></td>' % _(u"Services"))
        w(u'<td><a href="/inventory">%s</a></td>' % _(u"Inventaire"))
        w(u'</tr></table>')

    def display_services(self):
        rql = "Any S, H, P, D WHERE S is Service, S purpose P, S description D, S hosted_by H?"
        rset = self._cw.execute(rql)
        self.wview('table', rset, 'null')

def registration_callback(vreg):
    vreg.register(IndexView, clear=True)
