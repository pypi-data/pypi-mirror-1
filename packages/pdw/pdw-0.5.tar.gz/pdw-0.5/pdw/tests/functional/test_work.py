from pdw.tests import *

import pdw.model as model

class TestWork(TestController):
    
    def test_index(self):
        offset = url_for(controller='work', action='index')
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Works - Index')

    def test_read(self):
        id = self.fxt_work.id
        offset = url_for(controller='work', action='read', id=id)
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Works - %s' % self.fxt_work.title)
        res.mustcontain('Work: %s' % self.fxt_work.title) 

    def test_works_link(self):
        id = self.fxt_work.id
        offset = url_for(controller='work', action='read', id=id)
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Works - %s' % self.fxt_work.title)
        res.mustcontain('<h3>Creators')
        res.mustcontain(self.fxt_person.name)
        res.mustcontain('<h3>Items')
        res.click(self.fxt_performance.title)



