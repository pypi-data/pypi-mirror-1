# coding=utf8

import pkg_resources

import pdw.getdata.ngcoba2 as ngcoba2
import pdw.model as model

def _assert(exp):
    if exp:
        return #success
    #fail
    fail_txt = "not True %s" % (repr(exp))
    assert 0, fail_txt

def _assert_equals(exp1, exp2):
    if exp1 == exp2:
        return #success
    #fail
    fail_txt = "not equal %s and %s" % (repr(exp1), repr(exp2))
    assert 0, fail_txt

class TestAuthorEntryParser_ngcoba2(object):
    data_filename = 'tests/data/ngcoba2.txt'
    resource = pkg_resources.resource_stream('pdw', data_filename)
    loader = ngcoba2.Loader()
    parsed_data = loader.load(resource)

    @classmethod
    def teardown_class(self):
        model.repo.rebuild_db()

    # tests are numbered to give a rough running order
    
    def test_1_reading_test_file_ok(self):
        print self.parsed_data
        _assert(self.parsed_data)

    def test_2_name(self):
        _assert_equals(self.parsed_data[0]['name'], u'Ashcroft, Nell')

    def test_2_authorid(self):
        _assert_equals(self.parsed_data[0]['authorcode'], u'A005844')

    def test_2_bdate(self):
        _assert_equals(self.parsed_data[0]['raw_bdate'], u'1927 Jun 23')
        _assert_equals(self.parsed_data[0]['bdate'], u'1927-06-23')

    def test_2_ddate(self):
        _assert_equals(self.parsed_data[0]['raw_ddate'], u'?')
        _assert_equals(self.parsed_data[0]['ddate'], u'None')

    def test_3_name(self):
        _assert_equals(self.parsed_data[1]['name'], u'Ashcroft, Thomas')

    def test_3_ddate(self):
        _assert_equals(self.parsed_data[1]['raw_ddate'], u'1961 Jan 3')
        _assert_equals(self.parsed_data[1]['ddate'], u'1961-01-03')

    def test_3_work(self):
        _assert(self.parsed_data[1]['works'])
        _assert_equals(self.parsed_data[1]['works'][0], u'Text-book Of Modern Imperialism [n|1922]')
        _assert_equals(self.parsed_data[1]['works'][1], u'English Art And English Society [n|1936]')

    def test_3_aka_in_name(self):
        # Borhanuddin Mohammed ABBAS, aka Bi Ema ABBASA (M: 1911 - ?)
        _assert_equals(self.parsed_data[5]['name'], u'Abbas, Borhanuddin Mohammed')

    def test_3_ps_in_name(self):
        # A E ABBOT (ps)
        _assert_equals(self.parsed_data[6]['name'], u'Abbot, A E')

    def test_3_title_in_name(self):
        # Prof, Isaac ASIMOV
        _assert_equals(self.parsed_data[4]['name'], u'Asimov, Isaac [Prof]')

    def test_3_multiple_capitalised_names(self):
        # Charles ABBOTT, 1st Baron TENTERDEN
        _assert_equals(self.parsed_data[7]['name'], u'Abbott, Charles')

    def test_3_hard_name(self):
        # Lucius ANNAEUS Seneca, aka SENECA the Younger
        _assert_equals(self.parsed_data[8]['name'], u'Annaeus, Lucius')

    def test_3_name_see(self):
        # The PRESIDENT of the White Pass & Yukon Route (see: S H GRAVES)
        assert u'president' not in self.parsed_data[9]['name'].lower()

    def test_3_name_country(self):
        # P003893 Luella (nee?)Cole PRESSEY {US} (F: 1893 - ?)
        _assert_equals(self.parsed_data[9]['country'], u'US')

    def test_4_load_into_db(self):
        items = model.Item.query.all()
        _assert_equals(len(items), 0)
        resource = pkg_resources.resource_stream('pdw', self.data_filename)
        self.loader.load_to_db(resource)
        works = model.Work.query.all()
        assert len(works) > 0
        assert len(model.Person.query.all()) > 0
        _assert_equals(model.Person.query.filter_by(name=u'Ashton, Winifred').first().srcid, u'ngcoba::A005921')
