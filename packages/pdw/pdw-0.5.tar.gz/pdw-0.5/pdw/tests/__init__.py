"""Pylons application test package

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.

It registers the root directory of the project in sys.path and
pkg_resources, in case the project hasn't been installed with
setuptools. It also initializes the application via websetup (paster
setup-app) with the project's test.ini configuration file.
"""
import os
import sys

import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
from routes import url_for

__all__ = ['url_for', 'TestController']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

test_file = os.path.join(conf_dir, 'test.ini')
cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

# in a separate method so we can use it externally ...
# warning: must not have 'test' in the name
def create_fixtures():
    TestController.create_fixtures()

import pdw.model as model
model.binddb()
# clean the db before tests ...
model.repo.rebuild_db()


class TestController(object):

    def __init__(self, *args, **kwargs):
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)

    def setUp(self):
        self.create_fixtures()

    def tearDown(self):
        self.teardown_fixtures()
        model.Session.remove()

    fxt_name = u'Bach, Johann'
    fxt_pname = u'Casals, Pablo'
    fxt_title = u'Cello Suites'
    fxt_ptitle = u'Performance of Cello Suites'
    fxt_srcid=u'system.test::0000'

    # make class method so we can use outside ...
    @classmethod
    def create_fixtures(self):
        model.Session.remove()
        self.fxt_person = model.Person(name=self.fxt_name,
                srcid=self.fxt_srcid,
                birth_date=u'1685',
                death_date=u'1723',
                aka=u'The Greatest'
                )
        self.fxt_work = model.Work(title=self.fxt_title,
                date=u'1704',
                srcid=self.fxt_srcid)
        self.fxt_perf = model.Person(name=self.fxt_pname)
        self.fxt_work.persons.append(self.fxt_person)
        self.fxt_performance = model.Item(
                srcid=self.fxt_srcid,
                title=self.fxt_ptitle,
                date=u'1955',
                )
        self.fxt_work.items.append(self.fxt_performance)
        self.fxt_performance.persons.append(self.fxt_perf)
        self.fxt_work.extras = { 'source': u'made-up' }
        model.Session.commit()
        assert len(model.Person.query.all()) > 0
        model.Session.remove()

    @classmethod
    def teardown_fixtures(self):
        model.Session.remove()
        persons = model.Person.query.filter_by(name=self.fxt_name).all()
        persons = persons + model.Person.query.filter_by(name=self.fxt_pname).all()
        for p in persons:
            model.Session.delete(p)
        for w in model.Work.query.all():
            model.Session.delete(w)
        for w in model.Item.query.all():
            model.Session.delete(w)
        model.Session.commit()

