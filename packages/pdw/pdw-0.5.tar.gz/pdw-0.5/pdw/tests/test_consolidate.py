from pdw.tests import *

import pdw.model as model
import pdw.consolidate as c

class TestPerson(TestController):
    __test_id = u'consolidate_test'
    
    def setUp(self):
        p1 = model.Person(name=u'Mozart, Wolfgang Amadeus 0',
                birth_date='1756-01-27', death_date='1791-12-05',
                srcid=u'%s::0' % (self.__test_id)
                )
        for i in range(3):
            p = model.Person(name=u'Mozart, Wolfgang Amadeus',
                    birth_date='1756-01-27', death_date='1791-12-05',
                    srcid=u'%s::%s' % (self.__test_id, i+1)
                    )
            wrk = model.Work(title=u'Mozart Symphony No. 40', persons=[p],
                    srcid=u'%s::3-%s' % (self.__test_id, i+1)
                    )
            model.Item(title=u'Mozart Symphony No. 40', persons=[p],
                    works=[wrk],
                    srcid=u'%s::%s' % (self.__test_id, i+1)
                    )
            # another item which is the same really ...
            model.Item(title=u'Mozart Symphony No. 40', persons=[p],
                    srcid=u'%s::2-%s' % (self.__test_id, i+1)
                    )
            # another item which is completely different
            model.Item(title=u'More Mozart Symphonies', persons=[p1],
                    srcid=u'%s::3-%s' % (self.__test_id, i+1)
                    )

        model.Session.commit()
        model.Session.remove()

    def tearDown(self):
        # go for quick and dirty approach
        model.repo.rebuild_db()
        model.Session.clear()
        
    def test_consolidate_persons(self):
        q = model.Person.query.filter_by(name=u'Mozart, Wolfgang Amadeus')
        assert q.count() == 3
        c.consolidate_persons()
        q = model.Person.query.filter_by(name=u'Mozart, Wolfgang Amadeus')
        assert q.count() == 1, q.count()
        mozart = q.first()
        assert len(mozart.items) == 6, mozart.items
        assert len(mozart.works) == 3, mozart.works

    def test_items_to_works(self):
        c.items_to_works()
        model.Session.remove()
        # all type 3 items should now be attached to a common work ...
        title = u'More Mozart Symphonies'
        q = model.Item.query.filter_by(title=title)
        assert q.count() == 3, q.count()
        items = q.all()
        assert items[0].works, items[0].works

    def test_items_to_works_2(self):
        # all type 2 items consolidated: 3 works each with 2 items
        # will not be consolidate further as works are different (due to
        # different person)
        c.items_to_works()
        model.Session.remove()
        title = u'Mozart Symphony No. 40' 
        works = model.Work.query.filter_by(title=title).all()
        assert len(works) == 3, len(works)
        assert len(works[1].items) == 2, works[1].items
        assert len(works[0].items) == 2, [ (i.title, i.srcid) for i in
                works[0].items ]
        # persons=[p1],
        # srcid=u'%s::2-%s' % (self.__test_id, i+1)



