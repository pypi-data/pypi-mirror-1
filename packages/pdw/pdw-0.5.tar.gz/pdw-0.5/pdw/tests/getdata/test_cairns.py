import os
from StringIO import StringIO

from pdw.getdata.cairns import *
cachedir = os.path.join('cache', 'cairns')
# http://knowledgeforge.net/pdw/A1_sample.txt
sample_file = os.path.join(cachedir, 'A1_sample.txt')

class TestCairns:
    def test_1(self):
        parser = CairnsParser()
        outfobj = StringIO()
        # TODO: make this a decent test ...
        parser(open(sample_file), CairnsToCsv(outfobj))
        outfobj.seek(0)
        out = outfobj.read()
        assert len(out) > 0

