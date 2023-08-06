import pdw.tests

class TestHome(pdw.tests.TestController):
    
    def test_1(self):
        res = self.app.get('/') 
        res.mustcontain('Public Domain Works')
