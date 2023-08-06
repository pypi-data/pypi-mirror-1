from pdw.tests import *
import pdw.stats
import pdw.model as model

class TestStats:
    @classmethod
    def setup_class(self):
        TestController.create_fixtures()
    
    @classmethod
    def teardown_class(self):
        TestController.teardown_fixtures()
    
    def test_basic_info(self):
        results = pdw.stats.basic_info()
        assert results['count']['Work'] == 1
        assert results['count']['Person'] == 2
        bytype = results['work type']
        assert len(bytype[0]) == 3, bytype
        assert bytype[1] == [ 'Item', 'text', 1]

    def test_persons_by_item_counts(self):
        q = pdw.stats.persons_by_item_counts()
        out = q.execute().fetchall()
        print out
        assert len(out) == 1
        out[0][1] == u'Casals, Pablo'
        # count is 1
        out[0][2] == 1

    def test_by_year(self):
        years, cumulative = pdw.stats.by_year(model.Person.query,
                model.Person.birth_date_ordered, years=range(1600, 1950, 10))
        assert len(years) > 0
        mydict = dict(zip(years, cumulative))
        print mydict
        assert mydict[1680] == 0
        assert mydict[1690] == 1

    def test_cumulative_to_per_period(self):
        x = [ 1, 1, 2, 6 ]
        out = pdw.stats.cumulative_to_per_period(x)
        assert out == [ 1, 0, 1, 4 ], out

