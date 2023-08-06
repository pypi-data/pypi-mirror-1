from pdw.tests import *

import pdw.model as model
import pdw.search as search

class TestSearch:
    finder = search.Finder()

    @classmethod
    def setup_class(self):
        TestController.create_fixtures()

    @classmethod
    def teardown_class(self):
        TestController.teardown_fixtures()

    def test_search_work(self):
        out = self.finder.work(TestController.fxt_title)
        assert out

        out = self.finder.work(u'some random string')
        assert not out
        
    def test_search_person(self):
        out = self.finder.person(u'Bach')
        assert out
        out = self.finder.person(u'Casals, Pablo')
        assert out

    def test_get_work_for_item(self):
        title = TestController.fxt_title
        item = model.Item(title=title)
        work = self.finder.get_work_for_item(item)
        assert work.title == title


class TestTitle:
    t = search.Titlizer()
    ins = [
        '''"'Tis Pity She's a Whore":York Notes Advanced''',
        '"Adventures of Baron Munchhausen":The Screenplay:Applause Screenplay Series',
        'A Christmas Carol: Critical Edition',
        '"Antigone":Student Editions',
        'Anouilh Plays:"Antigone", "Leocardia", The "Waltz of the Toreadors", The "Lark", "Poor Bitos" (Bk. 1) :Methuen World'
        ]
    exps = [
        "'Tis Pity She's a Whore",
        'Adventures of Baron Munchhausen',
        'Christmas Carol, A',
        'Antigone',
        'Anouilh Plays',
        ]

    def test_simplify(self):
        for intitle, exp in zip(self.ins, self.exps):
            out = self.t.simplify(intitle)
            assert out == exp, out

    def test_norm(self):
        in1 = 'A Tree'
        out = self.t.norm(in1)
        assert out == 'Tree, A', out


import sqlalchemy.sql as sql
class TestQueryHelper:
    @classmethod
    def setup_class(self):
        TestController.create_fixtures()
        self.title = TestController.fxt_ptitle
        item = model.Item.query.filter_by(title=self.title).first()
        self.isbn13 = u'13481438149'
        item.extras[u'isbn13'] = self.isbn13
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(self):
        TestController.teardown_fixtures()

    def test_setupok(self):
        ouritem = model.Item.query.filter_by(title=self.title).first()
        assert ouritem.extras['isbn13'] == self.isbn13

    def test_extras(self):
        fromobj = search.QueryHelper.join_extras(model.item_table, u'isbn13', model.item_table)
        q = sql.select([model.item_table.c.id, model.extra_table.c.value],
            from_obj=[fromobj]
            )
        fullquery = q.where(model.extra_table.c.value==self.isbn13)
        print fullquery
        out = fullquery.execute().fetchall()
        assert len(out) == 1, out

        fullquery = q.where(model.extra_table.c.value=='afdjkfa')

        print fullquery
        out = fullquery.execute().fetchall()
        assert len(out) == 0, out
    
    def test_by_title(self):
        q = search.QueryHelper.by_item_title(model.Item.query, self.title)
        out = q.all()
        assert len(out) == 1, out

