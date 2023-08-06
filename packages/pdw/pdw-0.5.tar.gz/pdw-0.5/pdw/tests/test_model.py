from datetime import datetime

from pdw.tests import *

import pdw.model as model 
import pdw.model.sale


class TestFRBR(object):
    @classmethod
    def setup_class(self):
        self.fn = TestController.fxt_name
        self.pfn = TestController.fxt_pname
        self.title = TestController.fxt_title 
        self.ptitle = TestController.fxt_ptitle
        TestController.create_fixtures()

    @classmethod
    def teardown_class(self):
        TestController.teardown_fixtures()

    def test_artist(self):
        art2 = model.Person.query.filter_by(name=self.fn).one()
        assert art2.birth_date == '1685'
        assert art2.birth_date_normed == '1685'
        assert art2.birth_date_ordered == 1685
        assert art2.death_date == '1723'
        assert art2.death_date_normed == '1723'
        assert art2.death_date_ordered == 1723
        assert art2.aka == u'The Greatest'
        assert art2.srcid == TestController.fxt_srcid

    def test_work(self):
        work = model.Work.query.filter_by(title=self.title).one()
        assert self.title == work.title
        assert work.srcid == TestController.fxt_srcid
        assert work.date == '1704'
        assert work.date_normed == '1704'
        assert work.date_ordered == 1704
        assert self.fn == work.persons[0].name
        assert 1 == len(work.items)
        print work
        assert work.extras['source'] == 'made-up', work

    def test_item(self):
        rec = model.Item.query.filter_by(title=self.ptitle).one()
        assert self.title == rec.works[0].title
        assert rec.date == '1955'
        assert rec.date_normed == '1955'
        assert rec.date_ordered == 1955
        assert rec.persons[0].name == self.pfn
        assert rec.srcid == TestController.fxt_srcid

class TestSale(object):
    @classmethod
    def setup_class(self):
        self.fn = TestController.fxt_name
        self.pfn = TestController.fxt_pname
        self.title = TestController.fxt_title 
        self.ptitle = TestController.fxt_ptitle
        TestController.create_fixtures()
        item = model.Item.query.filter_by(title=self.ptitle).first()
        sale = pdw.model.sale.Sale()
        sale.item = item
        sale.price = 10.0
        sale.extras = {'abc': 1}
        model.Session.commit()

    @classmethod
    def teardown_class(self):
        for s in pdw.model.sale.Sale.query.all():
            model.Session.delete(s)
        TestController.teardown_fixtures()

    def test_sale(self):
        sale = pdw.model.sale.Sale.query.all()[0]
        assert sale.item is not None
        assert sale.price == 10.0
        assert sale.extras['abc'] == 1

