from pdw.tests import *

import pdw.model as model

class TestItem(TestController):
    
    def test_index(self):
        offset = url_for(controller='item', action='index')
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Items - Index')

    def test_read(self):
        id = self.fxt_performance.id
        offset = url_for(controller='item', action='read', id=id)
        res = self.app.get(offset) 
        res.mustcontain('Public Domain Works DB - Items - ')
        res.mustcontain('Item: %s' % self.fxt_performance.title)
        # res.mustcontain('Work: ')
        # res.mustcontain(self.fxt_performance.work.title)
        # res.mustcontain('Date: %s' % self.fxt_performance.performance_date)
        # res.mustcontain('Public Domain (EU)?</strong> YES!')

    def test_links(self):
        id = self.fxt_performance.id
        offset = url_for(controller='item', action='read', id=id)
        res = self.app.get(offset) 
        res.mustcontain('Item: %s' % self.fxt_performance.title)
        res.mustcontain('People')
        # TODO: fix this
        # res.mustcontain(self.fxt_person.name)


