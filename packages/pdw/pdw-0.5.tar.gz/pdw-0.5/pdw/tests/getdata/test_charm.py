import os 
from pdw.tests import *
import pdw.model as model

from pdw.getdata.charm import *

charmdata = CharmData()
fp_schubert_orig = charmdata.find_url("schubert_songs", 1)
fp_schubert = os.path.abspath('pdw/tests/data/charm.schubert_songs.html.cutdown')

fp_gray_orig = charmdata.find_url("columbia", 1)
fp_gray_columbia = os.path.abspath('pdw/tests/data/charm.columbia1.html.cutdown')
fp_italianhmv_green = os.path.abspath('pdw/tests/data/charm.green.html.cutdown')
#fp_gray_decca = os.path.abspath('pdw/tests/data/charm.decca1.html.cutdown')

class TestCharmDataSchubert:
    # avoid doing tests when no local data
    # To get local data do charm.download()
    __test__ =  os.path.exists(fp_schubert)

    @classmethod
    def setup_class(self):
        self.charm = charmdata

    @classmethod
    def teardown_class(self):
        model.repo.rebuild_db()
        model.Session.remove()

    def test_parse_schubert(self):
        parser = CharmParser('schubert_songs', '', open(fp_schubert))
        out = [ row for row in parser.get_parser() ]
        assert len(out) > 0, out
        rec1 = out[0]
        assert rec1['srcid'] == 'charm.schubert_songs::1'
        assert rec1['title'].startswith('Verkl'), rec1
        assert rec1['date'] == '1922', rec1
        assert rec1['extras']['original'].startswith('Sigrid'), rec1
        # weird one with a line break in a one line
        rec2 = out[-1]
        ## TODO: fix this up to be correct (see comment in main file)
        assert rec2['date'] == u'8900\xbd GD', rec2['date'].encode('utf8')
        # assert rec2['date'] == '1941/03/11', rec2

    def test_load_into_db(self):
        parser = CharmParser('schubert_songs', '', open(fp_schubert))
        recs = [ row for row in parser.get_parser() ]
        items = model.Item.query.all()
        assert len(items) == 0
        self.charm.load_into_db(recs)
        items = model.Item.query.all()
        assert len(items) > 0
        assert len(items[0].works) == 1
        assert len(model.Person.query.all()) == 1
        out = model.Item.query.filter_by(srcid=u'charm.schubert_songs::2')
        assert len(out.all()) == 1


class TestCharmDataGray:
    # avoid doing tests when no local data
    # To get local data do charm.download()
    __test__ =  os.path.exists(fp_gray_columbia)

    @classmethod
    def setup_class(self):
        self.charm = charmdata

    @classmethod
    def teardown_class(self):
        model.repo.rebuild_db()
        model.Session.remove()

    def test_parse_gray_columbia(self):
        parser = CharmParser('columbia', '', open(fp_gray_columbia))
        out = [ row for row in parser.get_parser() ]
        assert len(out) > 0, out
        headings = out[0].keys()
        assert u'matrix nr' in headings
        rec1 = out[0]
        assert rec1['srcid'] == 'charm.columbia::W230599'
        assert rec1['date'] == '1933-04-23'
        assert rec1['composer'] == ['Scarlatti'], rec1
        assert out[-1]['matrix nr'] == '25146'

    def test_load_into_db_gray_columbia(self):
        parser = CharmParser('columbia', '', open(fp_gray_columbia))
        recs = [ row for row in parser.get_parser() ]
        items = model.Item.query.all()
        assert len(items) == 0
        self.charm.load_into_db(recs)
        items = model.Item.query.all()
        assert len(items) > 0
        assert len(items[0].works) == 1


##class TestCharmDataItalianHmv:
##    # avoid doing tests when no local data
##    # To get local data do charm.download()
##    __test__ =  os.path.exists(fp_italianhmv_green)
    
##    def test_parse_italianhmv_green(self):
##        parser = CharmParser('green', '', open(fp_italianhmv_green))
##        out = [ row for row in parser.get_parser() ]
##        assert len(out) > 0, out
##        headings = out[0].keys()
##        assert u'matrix nr' in headings
##        rec1 = out[0]
##        assert rec1['date'] == '19-10-09'
##        assert rec1['composer'] == ['Cajoli'], rec1
##        assert rec1['composer'] == ['Cajoli'], rec1
##        assert rec1['artist'] == ['BANDA DELLA LEGIONE RR CARABINIERI DI ROMA'], rec1
##        assert rec1['category'] == ['Band records'], rec1
