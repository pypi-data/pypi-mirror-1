from cubicweb.selectors import implements, rql_condition
from cubicweb.web.component import RelatedObjectsVComponent

class SentMailVComponent(RelatedObjectsVComponent):
    """email sent by this person"""
    __regid__ = 'sentmail'
    __select__ = RelatedObjectsVComponent.__select__ & implements('Person') & rql_condition('X use_email EA, E sender EA')
    rtype = 'use_email'
    role = 'subject'
    order = 40
    # reuse generated message id
    title = _('contentnavigation_sentmail')

    def rql(self):
        """override this method if you want to use a custom rql query"""
        return 'Any E ORDERBY D DESC WHERE P use_email EA, E sender EA, E date D, P eid %(x)s'

class ThreadTopicVComponent(RelatedObjectsVComponent):
    """email in threads related to this topic"""
    __regid__ = 'threadtopic'
    __select__ = RelatedObjectsVComponent.__select__ & implements('Application') & rql_condition('E in_thread T, T topic X')
    rtype = 'topic'
    role = 'object'
    order = 40
    # reuse generated message id
    title = _('contentnavigation_mailtopic')

    def rql(self):
        """override this method if you want to use a custom rql query"""
        return 'Any E ORDERBY D DESC WHERE E date D, E in_thread T, T topic A, A eid %(x)s'

