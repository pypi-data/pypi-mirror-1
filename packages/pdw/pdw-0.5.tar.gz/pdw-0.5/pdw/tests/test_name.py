import pdw.name


class TestName:
    def test_parse_name_FL(self):
        name = u'Ludwig Van Beethoven'
        out = pdw.name.parse_name(name)
        assert out.ln == u'Beethoven'
        assert out.fns == ['Ludwig', 'Van']

    def test_parse_name_LF_with_extra_comma(self):
        out = pdw.name.parse_name('More, Sir Thomas,Saint')
        assert out.ln == 'More', out
        assert out.fns == ['Sir', 'Thomas']

    def test_parse_name_FL_normcase(self):
        name = u'Ludwig van BEETHOVEN'
        out = pdw.name.parse_name(name)
        assert out.ln == 'Beethoven', out

    def test_parse_name_LF_with_title(self):
        name = u'Chandos, John [Sir]'
        out = pdw.name.parse_name(name)
        assert out.ln == 'Chandos', out
        assert out.title == 'Sir', out

    def test_parse_name_FL_with_title(self):
        name = u'Sir John CHANDOS'
        out = pdw.name.parse_name(name)
        assert out.ln == 'Chandos', out
        assert out.title == 'Sir', out

    def test_parse_name_FL_with_title_2(self):
        name = u'Prof Benjamin AARON'
        out = pdw.name.parse_name(name)
        assert out.ln == 'Aaron', out
        assert out.title == 'Prof', out
        assert out.fns == ['Benjamin'], out
        assert str(out) == 'Aaron, Benjamin [Prof]'

    def test_parse_title_with_fullstop(self):
        name = 'Major. abc xyz'
        out = pdw.name.parse_name(name)
        assert out.title == 'Major', out.title

    def test_parse_title_with_fullstop_2(self):
        name = 'Xyz, Abc [Major.]'
        out = pdw.name.parse_name(name)
        assert out.title == 'Major', out.title

    def test_parse_name_FL_initials(self):
        name = 'Chekhov, A.P.'
        out = pdw.name.parse_name(name)
        assert out.ln == 'Chekhov'
        assert out.fns == ['A.', 'P.'], out

    def test_tostr(self):
        name = pdw.name.Name(ln='Beethoven', fns=['Ludwig', 'van'])
        exp = u'Beethoven, Ludwig van'
        out = pdw.name.name_tostr(name)
        assert out == exp, out

    def test_with_no_name(self):
        name = pdw.name.parse_name(' ')
        assert name.ln is '', name
        out = pdw.name.normalize(' ')
        assert out == '', out

    def test_surname(self):
        name = u'SCHUBERT'
        out = str(pdw.name.parse_name(name))
        assert out == 'Schubert'
