from datetime import timedelta
from os.path import dirname, join, abspath
from logilab.common.decorators import cached

from cubicweb import MultiSourcesError
from cubicweb.devtools import TestServerConfiguration, ApptestConfiguration, init_test_database
from cubicweb.devtools.testlib import CubicWebTC

#from unittest_querier_planner import do_monkey_patch, undo_monkey_patch

class ThreeSourcesConfiguration(ApptestConfiguration):
    @cached
    def sources(self):
        res = TestServerConfiguration.sources(self)
        res['extern'] = {'adapter':    'pyrorql',
                         'pyro-ns-id': 'extern',
                         'cubicweb-user': 'admin',
                         'cubicweb-password': 'gingkow',
                         'mapping-file': abspath(join(dirname(__file__), 'data', 'extern_mapping.py'))
                         #'base-url': '',
                         }
        res['extern2'] = {'adapter':    'pyrorql',
                         'pyro-ns-id': 'extern2',
                         'cubicweb-user': 'admin',
                         'cubicweb-password': 'gingkow',
                         'mapping-file': abspath(join(dirname(__file__), 'data', 'extern_mapping.py'))
                         #'base-url': '',
                         }
        if self._enabled_sources is None:
            return res
        return dict((uri, config) for uri, config in res.items()
                    if uri in self._enabled_sources)


class ExternalSourceConfiguration(TestServerConfiguration):
    @cached
    def sources(self):
        res = {'admin': {'login': 'admin', 'password': 'gingkow'}}
        res['system'] = {'adapter':     'native',
                         'db-driver':   'sqlite',
                         'db-name':     'tmpdb-extern',
                         'db-encoding': 'utf8',
                         'db-host':     '',
                         'db-user':     'admin',
                         'db-password': 'gingkow',
                         }
        return res

class External2SourceConfiguration(TestServerConfiguration):
    @cached
    def sources(self):
        res = {'admin': {'login': 'admin', 'password': 'gingkow'}}
        res['system'] = {'adapter':     'native',
                         'db-driver':   'sqlite',
                         'db-name':     'tmpdb-extern2',
                         'db-encoding': 'utf8',
                         'db-host':     '',
                         'db-user':     'admin',
                         'db-password': 'gingkow',
                         }
        return res

repo2, cnx2 = init_test_database(config=ExternalSourceConfiguration('data'))
cu = cnx2.cursor()
ep1eid = cu.execute('INSERT Project X: X name "Extern project 1"')[0][0]
ep1v1eid = cu.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Extern project 1"')[0][0]
ep2eid = cu.execute('INSERT Project X: X name "Extern project 2"')[0][0]
ep2v1eid = cu.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Extern project 2"')[0][0]
cnx2.commit()

repo3, cnx3 = init_test_database(config=External2SourceConfiguration('data'))
cu3 = cnx3.cursor()
e2p1eid = cu3.execute('INSERT Project X: X name "Extern2 project 1"')[0][0]
cnx3.commit()

# XXX, access existing connection, no pyro connection
from cubicweb.server.sources.pyrorql import PyroRQLSource
PyroRQLSource.get_connection = lambda x: x.uri == 'extern' and cnx2 or cnx3
# necessary since the repository is closing its initial connections pool though
# we want to keep cnx2 valid
from cubicweb.dbapi import Connection
Connection.close = lambda x: None

class BaseMSTC(CubicWebTC):
    config = ThreeSourcesConfiguration('data')

    def setUp(self):
        CubicWebTC.setUp(self)
        self.extern = self.repo.sources_by_uri['extern']
        # trigger import from external source since sqlite doesn't support
        # concurrent access to the database
        self.execute('Any P, V WHERE V? version_of P')
        self.execute('State X')
        self.maxeid = self.execute('Any MAX(X)')[0][0]
        self.ip1eid = self.execute('INSERT Project X: X name "Intern project 1"')[0][0]
        self.ip1v1eid = self.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Intern project 1"')[0][0]
        self.ip1t1eid = self.execute('INSERT Ticket X: X title "ticket project 1", X concerns P, X done_in V WHERE P eid %(p)s, V eid %(v)s',
                                     {'p': self.ip1eid, 'v': self.ip1v1eid})[0][0]
        self.ip2eid = self.execute('INSERT Project X: X name "Intern project 2"')[0][0]
        self.ip2v1eid = self.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Intern project 2"')[0][0]
        self.ip2t1eid = self.execute('INSERT Ticket X: X title "ticket project 2", X concerns P, X done_in V, X depends_on T WHERE P eid %(p)s, V eid %(v)s, T eid %(t)s',
                                     {'p': self.ip2eid, 'v': self.ip2v1eid, 't': self.ip1t1eid})[0][0]
        self.ip3eid = self.execute('INSERT Project X: X name "Intern project 3"')[0][0]
        self.commit()

    def extid2eid(self, extid, etype):
        return self.repo.extid2eid(self.extern, str(extid), etype, self.session)

    def fire_transition(self, eid, trname):
        e = self.execute('Any X WHERE X eid %(x)s', {'x': eid}, 'x').get_entity(0, 0)
        e.fire_transition(trname)

    def change_state(self, eid, stname):
        e = self.execute('Any X WHERE X eid %(x)s', {'x': eid}, 'x').get_entity(0, 0)
        e.change_state(stname)


class TwoSourcesTC(BaseMSTC):

    def test_projects_list(self):
        rset = self.execute('Project P')
        self.assertEquals(len(rset), 6)

    def test_nonregr1(self):
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip1eid}, 'x')
        self.assertEquals(rset.rows, [])
        self.change_state(self.ip1v1eid, 'published')
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip1eid}, 'x')
        self.assertEquals(len(rset.rows), 1)
        self.assertEquals(rset.rows[0][0], self.ip1eid)
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip2eid}, 'x')
        self.assertEquals(rset.rows, [])
        self.change_state(self.ip2v1eid, 'published')
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip2eid}, 'x')
        self.assertEquals(len(rset.rows), 1)
        # same test with entities from the external source
        iep1eid = self.extid2eid(ep1eid, 'Project')
        iep1v1eid = self.extid2eid(ep1v1eid, 'Project')
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': iep1eid}, 'x')
        self.assertEquals(rset.rows, [])
        # XXX don't work anymore since changing state is done by adding TrInfo which isn't currently
        #     imported from external sources
        self.assertRaises(MultiSourcesError, self.change_state, iep1v1eid, 'published')
        #self.change_state(iep1v1eid, 'published')
        # rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
        #                     {'x': iep1eid}, 'x')
        # self.assertEquals(len(rset.rows), 1, rset)
        # self.assertEquals(rset.rows[0][0], iep1eid)
        # iep2eid = self.extid2eid(ep2eid, 'Project')
        # iep2v1eid = self.extid2eid(ep2v1eid, 'Project')
        # rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
        #                     {'x': iep2eid}, 'x')
        # self.assertEquals(rset.rows, [])
        # self.change_state(iep2v1eid, 'published')
        # rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
        #                     {'x': iep2eid}, 'x')
        # self.assertEquals(len(rset.rows), 1)

    def test_nonregr2(self):
        ip2v1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.ip2v1eid}, 'x').get_entity(0, 0)
        rset = ip2v1.depends_on_rset()
        self.assertEquals(len(rset.rows), 1)
        self.assertEquals(rset.rows[0][0], self.ip1v1eid)

    def test_nonregr3(self):
        self.execute('Any V,DATE ORDERBY version_sort_value(N) '
                     'WHERE V num N, V prevision_date DATE, V version_of X, '
                     'V in_state S, S name IN ("planned", "dev", "ready"), X eid %(x)s',
                     {'x': self.ip1eid})

    def test_nonregr4(self):
        # test we can a change a ticket state (and implicitly its version'state by commiting
        self.fire_transition(self.ip1t1eid, 'start')
        self.commit()
        ip1v1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.ip1v1eid}, 'x').get_entity(0, 0)
        self.assertEquals(ip1v1.state, 'dev')

    def test_nonregr5(self):
        self.fire_transition(self.ip1t1eid, 'start')
        self.commit()
        rset = self.execute('Any X,U WHERE X in_state S, S name "in-progress", TR wf_info_for X, TR to_state S, TR owned_by U')
        self.failUnlessEqual(len(rset), 1, rset.rows)
        self.failUnlessEqual(rset[0], [self.ip1t1eid, self.session.user.eid])

    def test_nonregr7(self):
        rset = self.execute('Any B,TT,NOW - CD,PR,S,V '
                            'GROUPBY B,TT,CD,PR,S,V,VN '
                            'ORDERBY S, version_sort_value(VN), TT, priority_sort_value(PR) '
                            'LIMIT 1 '
                            'WHERE B type TT, B priority PR, B in_state S, B creation_date CD, B done_in V?, V num VN, B concerns P, P eid %s'
                            % self.ip1eid)
        rset.rows[0][4] = 'STATE'
        self.assertEquals(rset.rows, [[self.ip1t1eid, u'bug', timedelta(0), u'normal', 'STATE', self.ip1v1eid]])

    def test_nonregr8(self):
        self.execute('Any SN WHERE X has_text "toto", X in_state S, S name SN, X is IN (Project, Version, Transition)')

    def test_nonregr9(self):
        self.execute('DISTINCT Any AD,AE ORDERBY AE WHERE NOT S depends_on O, S eid %(x)s, O is Version, O in_state AD, AD name AE, AD modification_date AF',
                     {'x': self.ip1v1eid}, ('x',))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
