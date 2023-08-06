# coding=utf8
from pdw.getdata.ngcoba import *
import pdw.model as model

# TODO: run this off config file ...
cache = os.path.abspath('cache/ngcoba')

class TestAuthorEntryParser:
    parser = AuthorEntryParser()
    entry1 = 'A J van der AA (M: 1792 Dec 7 - 1857 Mar 21)'
    entry2 = 'Prof, Benjamin AARON {US} (M: 1915 Sep 25 - 2007 Aug 25)'
    entry3 = 'Alan Dean AARON {US} (M: 1960 Jan 30 - 2004 May 15 (wrongly 14))'
    entry4 = 'Maj, Waller ASHE (M: ? - ?)'
    entry5 = 'Leroy (F) AARONS {US} (M: 1933 Dec 8 - 2004 Nov 28)'
    entry6 = 'Slim AARONS (see: George Allen AARONS)'
    entry7 = 'S AATTO (?: 1855 - 1898)'
    entry8 = 'Johannes AAL (M: ? - 551)'
    entry9 = u'Yahya Taher ABDULLAH {EG} (M: 1942 or 1938 - 1981)'

    # TODO: here a tough one (both M and F!)
    entryXXX = u'Gordon (later Pepita) Langley HALL, Mrs SIMMONS (M to F: 1922 or 1937 Oct 16 - 2000 Sep 18 or 20)'

    def test_parse_line(self):
        out = self.parser.parse_line(self.entry1)
        print out
        assert out['name'] == u'Aa, A J Van Der'
        assert out['raw_bdate'] == '1792 Dec 7'

    def test_parse_line_2(self):
        out = self.parser.parse_line(self.entry2)
        print out
        # assert out['title'] == u'Prof'
        assert out['name'] == u'Aaron, Benjamin [Prof]'

    def test_parse_line_3(self):
        out = self.parser.parse_line(self.entry5)
        print out
        assert out['name'] == u'Aarons, Leroy F'
    
    def test_parse_line_4(self):
        out = self.parser.parse_line(self.entry7)
        print out
        assert out['name'] == u'Aatto, S'
        assert out['raw_bdate'] == '1855'

    def test_parse_entry(self):
        out = self.parser.parse_line(self.entry1)
        print out
        assert out['name'] == u'Aa, A J Van Der'

    def test_parse_2(self):
        out = self.parser.parse_line(self.entry6)
        # no match
        assert out is None

    def test_parse_3(self):
        out = self.parser.parse_line(self.entry4)
        print out
        assert out['ddate'] == 'None'

    def test_parse_4(self):
        out = self.parser.parse_line(self.entry8)
        print out
        assert out['bdate'] == 'None'
        assert out['ddate'] == '0551'

    def test_or_in_date(self):
        out = self.parser.parse_line(self.entry9)
        print out
        assert out['bdate'] == '1938 [Ambiguous date: "1942 or 1938"]'
        assert out['ddate'] == '1981'

    def test_parse_with_nee_and_weird_sex_string(self):
        # sex string of 'A' is the problem
        entry10 = u'Alice (<i>nee</i>)Erickson CHRISTGAU {US} (A: 1902 Nov 15 (or Feb 5) - 1977 Nov)'
        out = self.parser.parse_line(entry10)
        print out
        assert out['bdate'] == u'1902-11-15 [Ambiguous date: "1902 Nov 15 (or Feb 5)"]'

    def test_parse_5(self):
        # TODO breaks name parser part of AuthorEntryParser
        entry = u'John Pepper CLARK(-BEKEDEREMO) {NG} (M: 1935 - ?)'
        # out = self.parser.parse_line(entry)
        # assert out['bdate'].year == 1935
    
    def test_parse_with_bc(self):
        entry = 'SOPHOCLES (M: BC c496 - BC 406)'
        out = self.parser.parse_line(entry)
        print out
        assert out['raw_bdate'] == u'BC c496', out
        assert out['bdate'] == u"-0496 [Note 'circa': 'BC c496']", out
        assert out['name'] == u'Sophocles'

    def test_parse_wrongly_date(self):
        entry = u'L002627 (Percy) Wyndham LEWIS (M: 1884 (wrongly 1882 & 1886) Nov 18 - 1957 Mar 7)'
        out = self.parser.parse_line(entry)
        print out
        assert out['name'] == u'Lewis, (Percy) Wyndham'
        assert out['authorcode'] == u'L002627'
        assert out['bdate'] == u'1884-11-18'

    def test_parse_wrongly_date(self):
        entry = u'A005044 Lucius ANNAEUS Seneca, aka SENECA the Younger (M: BC c4 - 65)'
        out = self.parser.parse_line(entry)
        print out
        #TODO: Sort out parsing this complicated name correctly
#        assert out['name'] == u'Annaeus, Seneca Lucius' 
        assert out['bdate'] == u"-0004 [Note 'circa': 'BC c4']"
        assert out['ddate'] == u'0065'

    def test_parse_or_date(self):
        entry = u'B001112 Thomas Rocco BARBELLA {US} (M: 1922 (or 1919) Jan 1 (or Jun 22) - 1990 May 22 (or 23))'
        out = self.parser.parse_line(entry)
        print out
        assert out['bdate'] == u'1922-01-01 [Ambiguous date: "1922 (or 1919) Jan 1 (or Jun 22)"]'

    def test_parse_entry_4(self):
        entry = 'Denys James WATKINS-PITCHFORD (M: 1905 Jul (wrongly) 25 - 1990 Sep 8)'
        out = self.parser.parse_line(entry)
        print out
        assert out['bdate'] == '1905'

    def test_parse_entry_10(self):
        entry = u'(Percy) Wyndham LEWIS (M: 1923 - 1944)'
        out = self.parser.parse_line(entry)
        print out
        assert out['name'] == u'Lewis, Percy Wyndham', out['name']
        assert out['aka'] == u'Lewis, Wyndham', out['aka']

class TestLoader:
    loader = Loader()
    fn = os.path.join(cache, 'Aa.htm') 

    @classmethod
    def teardown_class(self):
        model.repo.rebuild_db()

    def test_isentry(self):
        in1 = '(&ps: Jan ORANJE)'
        assert not self.loader.isentry.match(in1)
        in2 = 'Thomas AABYE (M: 1756 - 1820)'
        assert self.loader.isentry.match(in2)
        in3 = ''
        assert not self.loader.isentry.match(in3)

    def test_load_lines(self):
        blocks = self.loader.load_lines(open(self.fn))
        out = [ self.loader.parse_entry(b) for b in blocks ]
        assert out[0]['name_line'] == 'A J van der AA (M: 1792 Dec 7 - 1857 Mar 21)', out[0]
        assert out[-1]['name_line'] == 'Khalilur Rahman AAZMI (M: 1927 - 1978)', out[-10:]
        assert len(out) == 184, len(out)

    def test_load(self):
        out = self.loader.load(open(self.fn))
        assert len(out) == 176, len(out)
        fn = out[0]['fullname']
        assert fn == u'A J van der AA', fn

    entry1 = '''Edward Sidney AARONS {US} (M: 1916 - 1975 Jun 16)
(&ps: Will B AARONS; Paul AYRES; Edward RONNS)
	Death In A Lighthouse (aka: The Cowl Of Doom) (ps: Edward RONNS) [f|1938]
	Murder Money (aka: $1,000,000 In Corpses) (ps: Edward RONNS) [f|1938]'''.split('\n')

    def test_parse_entry(self):
        out = self.loader.parse_entry(self.entry1)
        assert out['name_line'] == 'Edward Sidney AARONS {US} (M: 1916 - 1975 Jun 16)', out
        assert out['ps'] == ['Will B AARONS', 'Paul AYRES', 'Edward RONNS']
        assert len(out['works']) == 2, out['works']
        assert out['works'][0].startswith('Death In A')

    entry2 = '''George Allen AARONS {US} (M: 1916 Oct 29 - 2006 May 30)
(ps: Slim AARONS)'''.split('\n')

    def test_parse_entry_2(self):
        out = self.loader.parse_entry(self.entry2)
        assert out['ps'] == ['Slim AARONS'], out['ps']

    entry3 = '''SOPHOCLES (M: BC c496 - BC 406)
<A HREF="http://gutenberg.net/etext/14484">14484</A>  Aias [d|AG-BC450] (tr Lewis CAMPBELL) [1883/96]
  Ajax [d|AG-BC450] (tr R C TREVELYAN) [?]'''.split('\n')
    def test_parse_entry_3(self):
        out = self.loader.parse_entry(self.entry3)
        assert len(out['works']) == 2

    def test_dates(self):
        # Check test db is empty
        items = model.Item.query.all()
        assert len(items) == 0, len(items)

        self.loader.load_to_db(open(self.fn))
        works = model.Work.query.all()
        assert len(works) > 0
        assert len(model.Person.query.all()) > 0

        # Jens Christian AABERG {DK/US} (M: 1877 Nov 8 - 1970 Jun 22)
        person = model.Person.query.filter_by(name=u'Aaberg, Jens Christian').first()
        assert person.birth_date == u'1877 Nov 8', person.birth_date
        assert person.birth_date_normed == u'1877-11-08', person.birth_date_normed
        assert int(person.birth_date_ordered) == 1877, person.birth_date_ordered

        assert person.death_date == u'1970 Jun 22', person.death_date
        assert person.death_date_normed == u'1970-06-22', person.death_date_normed
        assert int(person.death_date_ordered) == 1970, person.death_date_ordered
        
        # Alan Dean AARON {US} (M: 1960 Jan 30 - 2004 May 15 (wrongly 14))
        person = model.Person.query.filter_by(name=u'Aaron, Alan Dean').first()

        assert person.death_date == u'2004 May 15 (wrongly 14)', person.death_date
        assert person.death_date_normed == u'2004-05-15', person.death_date_normed
        # TODO get this working in this case
#        assert int(person.death_date_ordered) == 2004, person.death_date_ordered
        

        
    


class TestWorkParser:
    work1 = 'Death In A Lighthouse (aka: The Cowl Of Doom) (ps: Edward RONNS) [f|1938]'
    work2 = '<a href="http://metalab.unc.edu/docsouth/authors.html">T</a>  The Light And Truth Of Slavery [a|1845]'
    work3 = 'Samlede Verker [3v|No-1943]'
    parser = WorkParser()

    def test_1(self):
        title, year = self.parser.parse(self.work1)
        assert title == 'Death In A Lighthouse (aka: The Cowl Of Doom)', title
        assert year == '1938', year

    def test_2(self):
        title, year = self.parser.parse(self.work2)
        assert title == 'The Light And Truth Of Slavery', title
        assert year == '1845'

    def test_3(self):
        title, year = self.parser.parse(self.work3)
        assert title == 'Samlede Verker'
        assert year == '1943'

    def test_4(self):
        title, year = self.parser.parse('The Steel Octopus [1961]')
        assert year == '1961'

    def test_5(self):
        title, year = self.parser.parse('*   Ferdinand De Soto [b|1873]')
        assert title == 'Ferdinand De Soto'

    def test_6(self):
        title, year = self.parser.parse('<a href="http://gutenberg.net/etext/16070">16070</a>,A The Empire Of Austria [n|?/?/1859]')
        assert year == '1859'

    def test_dots(self):
        work = '..The Operation Of Poisonous Agents.. (w J MORGAN) [n|1829]'
        title, year = self.parser.parse(work)
        assert title.startswith('The Operation Of Poisonous')
        assert year == '1829', year

    def test_8(self):
        work = u'Über Die Gesetzmässigkeit..  [n|Ge-1863]'
        title, year = self.parser.parse(work)
        assert year == '1863', year

    def test_9(self):
        work = u'<a href="http://gutenberg.net/etext/729">729</a> Hackers/Computer Revolution Heroes [1984?]'
        title, year = self.parser.parse(work)
        assert year == '1984', year



class TestNameParser:
    name1 = 'Jens Christian AABERG'
    name2 = 'Bertus(=Lambertus Jacobus Johannes) AAFJES'

    parser = NameParser()

    def test_1(self):
        out, aka = self.parser.parse(self.name1)
        assert out.ln == 'Aaberg', out
        assert out.fns == ['Jens', 'Christian'], out

    def test_2(self):
        out, aka = self.parser.parse(self.name2)
        assert out.ln == 'Aafjes', out
        # TODO: this does not seem right so we need to fix it ...
        assert out.fns == ['Bertus', '=Lambertus', 'Jacobus', 'Johannes'], out

    def test_with_nee(self):
        entry = u'Alice (<i>nee</i>)Erickson CHRISTGAU'
        out, aka = self.parser.parse(entry)
        assert str(out) == 'Christgau, Alice {nee} Erickson', out
        # TODO the fact we have aka = u'Christgau, Alice Erickson'


