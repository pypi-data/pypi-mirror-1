'''Processing BBC CAIRNS data.

Original code from James Casbon posted to pdb-discuss July 2007:

<http://lists.okfn.org/pipermail/pdb-discuss/2007-July/000241.html>
'''

import csv

class CairnsParser(object):
    buffer = None
    scanner = None

    def __call__(self, _file, scanner):
        self.scanner = scanner
        for line in _file:
            #print line
            line.rstrip('\n')
            if line.startswith('['):
                self.parse_buffer()
                self.buffer = ""

            if self.buffer is not None: 
                self.buffer += line

        if self.buffer:
            self.parse_buffer()
                
    def parse_buffer(self):
        # print "parse buffer", self.buffer
        if not self.buffer:
            return
        toks = self.buffer.split(']')
        for tok in toks:
            if tok.startswith('['):
                self.scanner.new_record(tok[1:])
            else:
                self.scanner.data(tok)


class CairnsToCsv(object):

    record = None
    writer = None

    def __init__(self, _file):
        self.writer = csv.writer(_file)

    def new_record(self, name):
        if self.record is not None:
            # print self.record
            self.writer.writerow(self.record)
        self.record = []

    def data(self, val):
        if self.record is not None:
            self.record.append(val)

