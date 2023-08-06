import os
import logging

import pdw.getdata.marc as marc
test_data_dir = 'pdw/tests/data/'

# Logging to screen on/off
if 0:
    logger = logging.getLogger('pdw.getdata.marc')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(ch)

class TestParserOpenLibrary(object):
    data_filename = os.path.join(test_data_dir, 'marc.cul.testdata')
    srcid_prefix =  u'marc.cul.test'

    parser = marc.ParserOpenLibrary()
    __records = []

    @classmethod
    def teardown_class(self):
        marc.model.Session.remove()

    def _get_records(self):
        if not self.__records:
            fo, srcid_prefix = file(self.data_filename), self.srcid_prefix
            for record in self.parser.parse(fo, srcid_prefix):
                self.__records.append(record)
        return self.__records
    
    def test_parser(self):
        records = self._get_records()
        assert len(records) == 79, len(records) # (2 of the 81 are duplicates)
        rec1 = records[0]
        print rec1.marc_source
        assert isinstance(rec1.title, unicode)
        assert rec1.title == u'Diagnostic histochemistry', rec1.title
        assert rec1.date == u'1970', rec1.date
        au = [ x.name for x in rec1.persons ]
        assert au == [u'Zugibe, Frederick T.'], rec1.persons
        assert rec1.persons[0].birth_date == u'1928', rec1.persons[0].birth_date

    def test_parser_3(self):
        records = self._get_records()
        rec2 = records[23]
        print rec2.marc_source
        au2 = [ x.name for x in rec2.persons ]
        # OL stuff ignores contributors ...
        assert au2 == ['Smith, B. J.'], au2
        assert rec2.persons[0].entity_type == u'person'

    def test_parser_4(self):
        records = self._get_records()
        rec = records[22]
        print rec.marc_source
        assert rec.persons[0].birth_date == u'1765'
        assert rec.persons[0].death_date == u'1844', rec.persons[0]

    def test_parser_5(self):
##        {'publishers': [u'Mosby'],
##         'pagination': u'xiv, 366 p.',
##         'lc_classifications': [u'RC78.7.C9 Z83'],
##         'title': u'Diagnostic histochemistry',
##         'dewey_decimal_class': [u'616.07/583'],
##         'notes': u'Bibliography: p. 332-349.',
##         'number_of_pages': 366,
##         'languages': [{'key': '/l/eng'}],
##         'lccn': [u'73117956'],
##         'isbn_10': [u'0801657024'],
##         'publish_date': '1970',
##         'publish_country': 'mou',
##         'authors': [{'birth_date': u'1928', 'personal_name': u'Zugibe, Frederick T.', 'name': u'Zugibe, Frederick T.', 'entity_type': 'person'}],
##         'by_statement': u'[by] Frederick T. Zugibe.',
##         'publish_places': [u'Saint Louis'],
##         'subjects': [u'Cytodiagnosis.', u'Histochemistry -- Technique.', u'Histocytochemistry.', u'Histological Techniques.']}
        records = self._get_records()
        assert len(records) == 79, len(records)
        rec = records[0]
        print rec.marc_source
        print rec
        assert rec.srcid == u'marc.cul.test::LCCN73117956.ISBN0801657024', rec.srcid
        assert rec.persons[0].name == u'Zugibe, Frederick T.'
        
        # TODO get this working
        # assert rec.type == u'text'

        # TODO get this working
        # assert rec.persons[0].role == u'author'

    def test_name(self):
        records = self._get_records()
        rec = records[1]
        print rec.marc_source
        print rec
        # TODO: reinstate this!
        # full stop should have gone
        # assert rec.persons[0].name == 'Kreisel, Georg', rec.persons[0].name

class TestParserPdw:
    data_filename = os.path.join(test_data_dir, 'marc.cul.testdata')
    srcid_prefix =  u'marc.cul.test'
    parser = marc.ParserPdw()

    @classmethod
    def teardown_class(self):
        marc.model.Session.remove()

    def _get_records(self):
        fo = file(self.data_filename)
        records = [ r for r in self.parser.parse(fo) ]
        return records
    
    def test_clean_year(self):
        yrs = [ 'c1790.', 'c179?' ]
        exps = [ 1790, 1799 ]
        for yr, exp in zip(yrs, exps):
            out = self.parser.clean_year(yr)
            assert out == exp

    def test_clean_author_dates(self):
        yrs = [ '1790-1850.', '1958-', '-1970', '1600']
        exps = [ (1790,1850), (1958,None), (None,1970), (1600,None)  ]
        for yr, exp in zip(yrs, exps):
            out = self.parser.clean_author_dates(yr)
            assert out == exp

    def test_parser(self):
        records = self._get_records()
        assert len(records) == 81, len(records)
        rec1 = records[0]
        assert isinstance(rec1.title, unicode)
        assert rec1.title == u'Diagnostic histochemistry', rec1.title
        assert rec1.date == u'1970', rec1
        au = [ x.name for x in rec1.persons ]
        assert au == [u'Zugibe, Frederick T.'], rec1.persons
        assert rec1.persons[0].birth_date == u'1928'

    def test_parser_2(self):
        records = self._get_records()
        au = [ x.name for x in records[5].persons ]
        assert au == ['Levy, J.', 'Budd, Keith.'], records[5].persons

    def test_parser_3(self):
        records = self._get_records()
        rec2 = records[23]
        au2 = [ x.name for x in rec2.persons ]
        assert au2 == [u'Smith, B. J.', u'Peters, R. J.',
            'Owen, Stephanie,'], au2

    def test_parser_4(self):
        records = self._get_records()
        rec = records[22]
        assert rec.persons[0].birth_date == u'1765'
        assert rec.persons[0].death_date == u'1844'

    def _show_records(self, records):
        count = 0
        for rec in records:
            print count, rec
            count += 1
