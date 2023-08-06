from cubicweb.selectors import implements
from cubicweb.web.views import autoform

class HostForm(autoform.AutomaticEntityForm):
    __select__ = implements('Host')

    def subject_hosted_by_vocabulary(self, rtype, limit=None):
        hosts = self.req.execute('Host H')
        devices = self.req.execute('Device D')
        if hosts:
            lst = [ (u'Hosts', None) ] + [ (e.view('combobox'), e.eid)
                                           for e in hosts.entities() ]
        if device:
            lst+= [ (u'Devices', None)]+ [ (e.view('combobox'), e.eid)
                                           for e in devices.entities() ]
        return lst
