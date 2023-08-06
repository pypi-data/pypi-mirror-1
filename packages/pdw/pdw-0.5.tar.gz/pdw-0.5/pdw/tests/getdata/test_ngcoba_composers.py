import datetime

import pdw.getdata.ngcoba_composers

# parse composer list
# assume this is run from trunk
path_to_composers_file = './data/composers.txt'

class TestParseComposers:

    parser = pdw.getdata.ngcoba_composers.ComposerFileParser()

    def test_parse_date(self):
        in1 = 'c1705'
        out1, errors = self.parser.parse_date(in1)
        exp1 = datetime.date(1705, 1, 1)
        assert out1 == exp1, out1

    def test_parse_date_2(self):
        in2 = ' 1877 Nov 8'
        out2, errors = self.parser.parse_date(in2)
        exp2 = datetime.date(1877, 11, 8)
        assert out2 == exp2

    def test_parse_date_3(self):
        in1 = '? '
        out1, errors = self.parser.parse_date(in1)
        exp1 = None
        assert out1 == exp1

    def test_parse_date_with_or(self):
        in1 =  '1942 or 1938'
        out1, errors = self.parser.parse_date(in1)
        assert out1 == None
        assert len(errors) == 1

    def test__sections(self):
        line = 'Jens Christian AABERG, * 1877 Nov 8, + 1970 Jun 22'
        out = self.parser._sections(line)
        assert out['fullname'] == 'Jens Christian AABERG'

    def test__parse_name_1(self):
        name = 'Jens Christian AABERG'
        ln, fn, alias = self.parser._parse_name(name)
        assert ln == 'AABERG'
        assert fn == 'Jens Christian'
        assert alias == ''

    def test__parse_name_2(self):
        name = 'Sarah Fuller (nee)Flower ADAMS (&ps: [Sarah FLOWER]; [S Y])'
        ln, fn, alias = self.parser._parse_name(name)
        assert ln == 'ADAMS'
        assert fn == 'Sarah Fuller (nee)Flower'
        assert alias == '&ps: [Sarah FLOWER]; [S Y]'

    def test_parse_line(self):
        line = 'Jens Christian AABERG, * 1877 Nov 8, + 1970 Jun 22'
        out = self.parser.parse_line(line)
        assert out['lname'] == 'AABERG'
        assert out['fname'] == 'Jens Christian'
        assert out['bdate'] == datetime.date(1877, 11, 8)
        assert out['ddate'] == datetime.date(1970, 6, 22)
    
    def test_parse_line_2(self):
        line = "Alphonso Giuseppe Giovanni Roberto d'ABRUZZO (ps: Robert ALDA), * 1914 Feb 26, + 1986 May 3"
        out = self.parser.parse_line(line)

    def test_parse_line_3(self):
        line = 'Emanuel AARONS, * ?, + ?'
        out = self.parser.parse_line(line)
        assert out['lname'] == 'AARONS'
        assert out['bdate'] == None

    def test_parse_line_4(self):
        line = 'Prof, John (Mervyn) ADDISON, aka Jock ADDISON, * 1920 Mar 16, + 1998 Dec 7'
        out = self.parser.parse_line(line)
        assert out['lname'] == 'ADDISON'
        assert out['extra'] == ' aka Jock ADDISON,'

    def test_parse_file(self):
        ff = file(path_to_composers_file)
        count = 0
        error = False
        for line in ff:
            try:
                out = self.parser.parse_line(line)
            except Exception, inst:
                print count
                print inst
                print line
                error = True
            count += 1
        assert error == False

