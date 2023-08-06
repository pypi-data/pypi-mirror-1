"""sysinfo web user interface"""

from cubicweb.web import uicfg
from cubicweb.web.views.urlrewrite import SimpleReqRewriter


class SysinfoSimpleReqRewriter(SimpleReqRewriter):
    """handle main entry points::

    /services : list of services

    /inventory : inventory

    /applications : application list
    """
    rules = [
        ('/services', dict(vid='services',rql='Service S')),
        ('/inventory', dict(vid='devices',rql='Device D')),
        ('/applications', dict(vid='applications',rql='Application D')),
        ]

uicfg.autoform_section.tag_subject_of(('Application', 'has_instance', '*'),
                                        'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Service', 'has_entry_point', '*'),
                                        'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Devide', 'made_of', '*'),
                                        'main', 'attributes')
