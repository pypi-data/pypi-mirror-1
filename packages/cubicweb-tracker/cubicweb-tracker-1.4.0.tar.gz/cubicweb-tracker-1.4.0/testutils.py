"""some utilities for testing tracker security

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.devtools import BaseApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb import Unauthorized, ValidationError

def ptransitions(entity):
    return sorted(tr.name for tr in entity.possible_transitions())

def create_project_rql(pname, description=None):
    return 'INSERT Project X: X name %(name)s, X description %(descr)s', \
           {'name': unicode(pname), 'descr': unicode(description)}

def create_version_rql(num, pname):
    return 'INSERT Version X: X num %(num)s, X version_of P '\
           'WHERE P name %(name)s', \
           {'num': unicode(num), 'name': unicode(pname)}

def create_ticket_rql(title, pname):
    return 'INSERT Ticket X: X title %(title)s, X concerns P '\
           'WHERE P name %(name)s', \
           {'title': unicode(title), 'name': unicode(pname)}


class TrackerTCMixIn(object):

    def create_project(self, pname, description=None):
        return self.execute(*create_project_rql(pname, description))

    def create_version(self, num, pname='cubicweb'):
        return self.execute(*create_version_rql(num, pname))

    def create_ticket(self, title, vnum=None, pname='cubicweb'):
        rset = self.execute(*create_ticket_rql(title, pname))
        if vnum:
            self.execute('SET X done_in V WHERE X eid %(x)s, V num %(num)s',
                         {'x': rset[0][0], 'num': vnum})
        return rset

    def grant_permission(self, project, group, pname, plabel=None, etype='Project'):
        """insert a permission on a project. Will have to commit the main
        connection to be considered
        """
        pname = unicode(pname)
        plabel = plabel and unicode(plabel) or unicode(group)
        peid = self.session.unsafe_execute(
            'INSERT CWPermission X: X name %%(pname)s, X label %%(plabel)s,'
            'X require_group G, '
            'P require_permission X '
            'WHERE G name %%(group)s, P is %s, P name %%(project)s' % etype,
            locals())[0][0]
        return peid

    def assertModificationDateGreater(self, entity, olddate):
        entity.pop('modification_date', None)
        self.failUnless(entity.modification_date > olddate)

    def assertPossibleTransitions(self, entity, expected):
        self.assertListEquals(ptransitions(entity), sorted(expected))


class TrackerBaseTC(TrackerTCMixIn, CubicWebTC):
    def setup_database(self):
        self.cubicweb = self.request().create_entity('Project', name=u'cubicweb',
                                        description=u"cubicweb c'est beau")


class SecurityTC(TrackerTCMixIn, CubicWebTC):
    repo_config = BaseApptestConfiguration('data')
    _initialized = False
    def setUp(self):
        CubicWebTC.setUp(self)
        self.__cnxs = {'admin': self.cnx}
        # trick to avoid costly initialization for each test
        if not SecurityTC._initialized:
            # implicitly test manager can add some entities
            self.__class__.cubicweb = self.execute(*create_project_rql("cubicweb")).get_entity(0, 0)
            self.execute(*create_project_rql("projet2"))
            self.execute('INSERT CWGroup X: X name "cubicwebdevelopers"')
            self.execute('INSERT CWGroup X: X name "cubicwebclients"')
            self.grant_permission('cubicweb', 'cubicwebdevelopers', u'developer')
            self.grant_permission('cubicweb', 'cubicwebclients', u'client')
            self.commit()
            self.create_user('stduser')
            self.create_user('staffuser', groups=('users', 'staff',))
            self.create_user('prj1developer', groups=('users', 'cubicwebdevelopers',))
            self.create_user('prj1client', groups=('users', 'cubicwebclients'))
            self.maxeid = self.execute('Any MAX(X)')[0][0]
            #SecurityTC._initialized = True
            cachedperms = self.execute('Any UL, PN WHERE U has_group_permission P, U login UL, P label PN')
            self.assertEquals(len(cachedperms), 2)
            self.assertEquals(dict(cachedperms),
                              {'prj1developer': 'cubicwebdevelopers', 'prj1client': 'cubicwebclients'})

    def mylogin(self, user):
        if not user in self.__cnxs:
            self.__cnxs[user] = self.login(user)
        return self.__cnxs[user]

    def _test_tr_fail(self, user, x, trname):
        cnx = self.mylogin(user)
        try:
            entity = cnx.request().entity_from_eid(x)
            # if the user can't see entity x, Unauthorized is raised, else if he
            # can't pass the transition, Validation is raised
            self.assertRaises((Unauthorized, ValidationError),
                              entity.fire_transition, trname)
        finally:
            cnx.rollback()

    def _test_tr_success(self, user, x, trname):
        cnx = self.mylogin(user)
        try:
            entity = cnx.request().entity_from_eid(x)
            entity.fire_transition(trname)
            cnx.commit()
        except:
            cnx.rollback()
            raise

