from pdw.tests import *

import pdw.controllers.person
import pdw.model.frbr

class TestReadableName(TestController):
    test_strings = [
        # format: (readable_id, name),
        (u'Schubert', u'Schubert'),
        (u'Franz_Schubert', u'Schubert, Franz'),
        (u'A_J_Van_Der_Aa', u'Aa, A J van der'),
        ]

    def _test_encode(self, test_number):
        person = pdw.model.frbr.Person.by_name(self.test_strings[test_number][1])
        out = person.readable_id
        correct_out = self.test_strings[test_number][0]
        assert out, correct_out

    def _test_decode(self, test_number):
        out = pdw.model.frbr._decode_person_readable_id(self.test_strings[test_number][0])
        correct_out = self.test_strings[test_number][1]
        assert out, correct_out

    def test_1_basic_encode(self):
        self._test_encode(0)

    def test_1_basic_decode(self):
        self._test_decode(0)

    def test_2_round_trips(self):
        for test_number in range(2):
            plain = self.test_strings[test_number][1]
            person = pdw.model.frbr.Person.by_name(plain)
            encoded = person.readable_id
            correct_encoded = self.test_strings[test_number][0]
            assert encoded, correct_encoded

            decoded = pdw.model.frbr._decode_person_readable_id(encoded)
            assert decoded == plain

    def test_3_readable_id(self):
        readable_id = self.fxt_person.readable_id
        offset = url_for(controller='person', action='read', id=readable_id)
        res = self.app.get(offset)
        assert 'Person: %s' % self.fxt_person.name in res, res

    def test_3_read_list(self):
        offset = url_for(controller='person', action='list', id=None)
        res = self.app.get(offset)
        readable_id = self.fxt_person.readable_id
        reqd = '<a href="/person/read/%s">%s </a>' % (readable_id, self.fxt_person.name)
        assert reqd in res, res
