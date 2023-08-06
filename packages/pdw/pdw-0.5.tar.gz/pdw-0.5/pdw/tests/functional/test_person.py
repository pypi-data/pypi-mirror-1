from pdw.tests import *

import pdw.model as model

class TestPerson(TestController):
    @classmethod
    def create_fixtures(self):
        TestController.create_fixtures()
        self.db_additions = []

        self.john = model.Person(name=u'Kennedy, John F.')
        self.sean = model.Person(name=u"Dhonncha, Se\xc3\xa1n. 'Ac")
        self.arthur = model.Person(name=u'Griffiths, Arthur [Major.]')
        self.db_additions.extend([self.john, self.sean, self.arthur])
        
        model.Session.commit()
    
    @classmethod
    def teardown_fixtures(self):
        TestController.teardown_fixtures()
        for addition in self.db_additions:
            model.Session.delete(addition)
        model.Session.commit()
    
    def test_index(self):
        offset = url_for(controller='person', action='index')
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Persons - Index')
        assert 'Search' in res, res

    def test_read_404(self):
        offset = url_for(controller='person', action='read', id=0)
        res = self.app.get(offset, status=404)

    def test_read(self):
        id = self.fxt_person.id
        offset = url_for(controller='person', action='read', id=id)
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Persons - %s' %
                self.fxt_person.name)
        res.mustcontain('Person: %s' % self.fxt_person.name)
        # res.mustcontain('Date of Death:')
        # res.mustcontain(self.fxt_person.source)
        # res.mustcontain('Works in Public Domain: ')

    def _test_works_link(self):
        id = self.fxt_person.id
        offset = url_for(controller='person', action='read', id=id)
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Persons - %s' %
                self.fxt_person.name)
        res.mustcontain('<h3>Works')
        res.mustcontain(self.fxt_work.title)
        res.mustcontain('<h3>Items')
        res.click(self.fxt_performance.title())

    def test_readable_urls(self):
        assert self.fxt_person.readable_id == 'Johann_Bach'
        matches = model.frbr.get_persons_matching_readable_id_query('Johann_Bach').all()
        assert len(matches) == 1
        assert matches[0].name == u'Bach, Johann'

        assert self.john.readable_id == 'John_F._Kennedy', self.john.readable_id
        matches = model.frbr.get_persons_matching_readable_id_query('John_F._Kennedy').all()
        assert len(matches) == 1
        assert matches[0].name == u'Kennedy, John F.'

        # TODO Get this working
##        assert self.arthur.readable_id == 'Arthur_%255BMajor.%255D_Griffiths', self.arthur.readable_id
##        matches = model.frbr.get_persons_matching_readable_id_query(self.arthur.readable_id).all()
##        assert len(matches) == 1
##        assert matches[0].name == u'Griffiths, Arthur [Major.]'

    def test_readable_urls_complicated(self):
        name_encoded = 'Se%C3%83%C2%A1n._%27Ac_Dhonncha'
        name_lastfirst = u"Dhonncha, Se\xc3\xa1n. 'Ac"
        
        assert self.sean.readable_id == name_encoded
        
        name_decoded = model.frbr._decode_person_readable_id(name_encoded)
        assert name_decoded == name_lastfirst
        
        matches = model.frbr.get_persons_matching_readable_id_query('Se%C3%83%C2%A1n._%27Ac_Dhonncha').all()
        assert len(matches) == 1
        assert matches[0].name == name_lastfirst, matches[0].name

    def test_person_link(self):
        offset = url_for(controller='person', action='list', id=0)
        res = self.app.get(offset)
        res.mustcontain('Public Domain Works DB - Persons - Index')
        res.mustcontain("Dhonncha, Se\xc3\x83\xc2\xa1n. \'Ac")


