from pdw.tests import *

import pdw.model as model 
import pdw.serialize

class TestSerialize:
    serializer = pdw.serialize.SQLAlchemy()

    @classmethod
    def setup_class(self):
        TestController.create_fixtures()
        self.newname = u'serialize-test'

    @classmethod
    def teardown_class(self):
        TestController.teardown_fixtures()
        person = model.Person.query.filter_by(name=self.newname).first()
        if person:
            model.Session.delete(person)
            model.Session.commit()
            model.Session.remove()
        model.repo.rebuild_db()

    def test_0_to_dict(self):
        name = TestController.fxt_name
        art = model.Person.query.filter_by(name=name).one()
        out = self.serializer.to_dict(art)
        assert out['name'] == name
        assert out['birth_date'] == '1685'

    def test_1_from_dict(self):
        mydict = {
            'name': self.newname,
            'birth_date': '1865',
            }
        out = self.serializer.from_dict(mydict, model.Person)
        model.Session.commit()
        assert out.name == self.newname
        assert out.birth_date == '1865'
        model.Session.clear()

    def test_2_form_dict_with_primary_key(self):
        name = TestController.fxt_name
        art = model.Person.query.filter_by(name=name).one()
        mydict = {
            'id': art.id,
            }
        out = self.serializer.from_dict(mydict, model.Person)
        assert out == art, out
        model.Session.clear()


import os
import shutil
import tempfile
import simplejson
from StringIO import StringIO
class TestDumper(object):
    dumper = pdw.serialize.Dumper([
        model.Person,
        model.Work,
        model.Item,
        model.WorkItem,
        model.WorkPerson,
        model.ItemPerson,
        model.Extra
        ],
        items_per_file=1,
        )
    tmpdir = os.path.join(tempfile.gettempdir(), 'test-dumper')

    @classmethod
    def setup_class(self):
        # 2009-05-12 something seems to not be cleaning up properly ...
        model.repo.rebuild_db()
        TestController.create_fixtures()
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    @classmethod
    def teardown_class(self):
        TestController.teardown_fixtures()

    def test_0_dump(self):
        myout = StringIO()
        self.dumper.dump(myout)
        myout.seek(0)
        out = simplejson.load(myout)
        print out
        assert 'Work' in out
        assert len(out['Work']) == 1

    def test_1_load(self):
        myout = StringIO()
        self.dumper.dump(myout)
        myout.seek(0)
        model.repo.rebuild_db()
        assert len(model.Work.query.all()) == 0
        self.dumper.load(myout)
        self._check_load()

    def _check_load(self):
        assert len(model.Work.query.all()) == 1
        assert len(model.Item.query.all()) == 1
        name = TestController.fxt_name
        art = model.Person.query.filter_by(name=name).one()
        assert art.birth_date == '1685'

    def test_2_dump_and_load(self):
        self.dumper.dump(self.tmpdir)
        fns = sorted(os.listdir(self.tmpdir))
        print fns
        assert len(fns) == 8, len(fns)

        model.repo.rebuild_db()
        self.dumper.load(self.tmpdir)
        self._check_load()

