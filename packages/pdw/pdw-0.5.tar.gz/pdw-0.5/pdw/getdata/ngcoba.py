import os
import re
import logging
from xml.dom.minidom import parse
import BeautifulSoup as bs

from pdw.name import titles

logger = logging.getLogger('getdata.ngcoba')

class AuthorEntryParser(object):
    def __init__(self):
        # will ignore entries such as:
        # P AARTSZ (see: Anton <A HREF="pa.htm">PA</A>NNEKOEK)
        # but this is OK because pseudonym is listed with main entry
        titles_str = str('|'.join(titles))
        self.line_regex = """
        (?P<authorcode>[A-Z]\d+\s)?
        (?:(?P<title>%(titles)s),)?
        (?P<fullname> [^{]+ )\s+
        (?P<country>[^(]*)
        (?# start of dates)
        (?:
            \(
            (?P<sex>[A|?|M|F]):\s*
            (?:(?P<bdate> [^-]+))
            \s-\s
            (?: (?P<ddate> .+))
            \)
        )
        """ % {'titles':titles_str}
        # (?P<extra> (?:(?:(?!\s\() [^,]+) , )* )
        self.line_pat = re.compile(self.line_regex, re.VERBOSE)

    def parse_line(self, line):
        mat = self.line_pat.match(line)
        if mat is None:
            return None
        sections = {}
        sections['authorcode'] = mat.group('authorcode')
        if sections['authorcode']:
            sections['authorcode'] = sections['authorcode'].strip()
        sections['fullname'] = mat.group('fullname')
        name, name_aka_str = NameParser().parse(mat.group('fullname'))
        name.title = mat.group('title')
        sections['name'] = name.norm()
        sections['aka'] = name_aka_str
        sections['raw_bdate'] = mat.group('bdate')
        sections['bdate'] = OurDateParser().parse(sections['raw_bdate'])
        sections['raw_ddate'] = mat.group('ddate')
        sections['ddate'] = OurDateParser().parse(sections['raw_ddate'])
        sections['country'] = CountryParser().parse(mat.group('country'))

        # Cope with errant ngcoba2 records with duplicate authorcodes
        if sections['authorcode'] and \
           (sections['authorcode'] == u'B007808' and sections['raw_bdate'] == u'1688') or \
           (sections['authorcode'] == u'N000777' and sections['fullname'] == u'John PETERS') or \
           (sections['authorcode'] == u'R002268' and sections['country'] == u'CA'):
            sections['authorcode'].append("a")
        
        return sections

from swiss.date import DateutilDateParser
class OurDateParser(DateutilDateParser):

    def parse(self, datestring):
        try:
            qualifier = None

            # Cope with the case with '1942 or 1938'
            ormatch = re.match('(\d+) or (\d+)', datestring)
            if ormatch:
                # use the 2nd date
                qualifier = 'Ambiguous date: "%s"' % datestring
                datestring = ormatch.group(2)

            # Cope with the case with '(or Jun 22)'
            ormatch = re.match('(.*)\(or[^)]+\)(.*)', datestring)
            if ormatch:
                # remove the '(or 5)'
                qualifier = 'Ambiguous date: "%s"' % datestring
                datestring = ''.join(ormatch.groups())

                # check for another group the same
                ormatch = re.match('(.*)\(or[^)]+\)(.*)', datestring)
                if ormatch:
                    datestring = ''.join(ormatch.groups())

            # Cope with '(wrongly Dec 14)'
            if 'wrongly' in datestring:
                # remove the '(wrongly 14)'
                match = re.match('(.*)\(wrongly[^)]+\)(.*)', datestring)
                if not match:
                    # remove 'June (wrongly) 14'
                    match = re.match('(.*) \w+ \(wrongly\).*', datestring)
                    '(.*) \w+ \(wrongly\).*'
                if match:
                    datestring = ''.join(match.groups())
                else:
                    assert "Couldn't handle 'wrongly' in: '%s'" % datestring

            # Get parsing done by main parser in date.py
            flexidate = DateutilDateParser.parse(self, datestring)

            # Add qualifiers processed in this method
            if flexidate and qualifier:
                flexidate.qualifier += qualifier

            # Convert to standardised string
            flexidate_str = unicode(flexidate)
        except Exception, inst:
            logger.warn("Ignoring date due to exception %s exception: '%s'", repr(datestring), inst)
            flexidate_str = u''
        return flexidate_str
        
from pdw.name import Name, NameParserBase, name_tostr
class NameParser(NameParserBase):
    def parse(self, fullname):
        fullnames = []
        # Cope with brackets e.g. '(Percy)'
        without_match = re.match('(.*) ?\([^)]+\) ?(.*)', fullname)
        if without_match:
            without = ' '.join(without_match.groups()).strip()
            with_match = re.match('(.*) ?\(([^)]+)\) ?(.*)', fullname)
            if with_match:
                with_ = ' '.join(with_match.groups()).strip()
            else:
                with_ = fullname
            fullnames = [with_]
            fullnames.append(without)

        if fullnames:
            name_ = NameParserBase.parse(self, fullnames[0])
            aka_names_str = []
            for fullname in fullnames[1:]:
                aka_name = NameParserBase.parse(self, fullname)
                aka_names_str.append(unicode(aka_name))
            aka_names_str = ';'.join(aka_names_str)
            return name_, aka_names_str
        else:
            return NameParserBase.parse(self, fullname), None
    
    def _toparts(self, fullname):
        # Cope with 'nee' TODO: deal with it better ...
        fullname = fullname.replace('(<i>nee</i>)', '{nee}')
        fullname = fullname.replace('(<i>ne<i>)', '{nee}')
        fullname = fullname.replace('<i>nee</i>', '{nee}')
        fullname = fullname.replace('<i>ne</i>', '{nee}')
        
        # Cope with ', aka' section
        if ', aka' in fullname:
            fullname = fullname[:fullname.find(', aka')]

        name = Name()

        # Search for first word of 2+ letters all caps        
        match_obj = re.match('(?P<fns>.*?)(?P<ln> [A-Z]{2,20})(.*)', fullname)
        if not match_obj:
            # Search for final word of 1+ letters all caps
            match_obj = re.match('(?P<fns>.+)?(?P<ln> [A-Z]+)', fullname)
            if not match_obj:
                # Search for only word of 1+ letters all caps
                match_obj = re.match('(?P<fns>)(?P<ln>[A-Z]+)$', fullname)


        # Build name object
        if match_obj:
            name.ln = match_obj.group('ln')
            fns = match_obj.group('fns')
            if fns is not None:
                name.fns = fns.split()
            
        return name

class CountryParser(object):
    country_pat = '.*{(?P<country>.*)}.*'
    country_re = re.compile(country_pat)
    
    def parse(self, country_str):
        if not country_str.strip():
            return None
        match_object = self.country_re.match(country_str)
        if not match_object:
            logger.warn('Failed to match country string: %s', repr(country_str))
            return None
        return match_object.group('country')            

class WorkParser(object):
    work_pat = r"""
        (?P<gutenberg> <a.+</a>(\S+)?\s+)?
        (?:[*['.])*\s*
        (?P<title>[$(\w].*)\s*
        (?# unfortunately the ps: never matches ... )
            (\(ps:[^)]+\))?\s*
        \[ (.*\D)?(?P<year>(\d+|\?))(?P<date_qualifier>\?)? \]
        """
    work_re = re.compile(work_pat, re.VERBOSE | re.UNICODE)

    def parse(self, work_str):
        mat = self.work_re.match(work_str)
        if mat is None:
            logger.warn('Failed to match work string: %s', repr(work_str))
            return (None, None)
        title = mat.group('title').strip()
        year = mat.group('year')
        if '(ps:' in title:
            title = title[0:title.index('(ps:')].strip()
        if year == '?':
            year = None
        return (title, year)

# for loading and parsing ngcoba data
class Loader(object):
    isentry = re.compile('^\\w')

    def load(self, fileobj):
        logger.info('START Loading and parsing a file')
        raw_entries = self.load_lines(fileobj)
        results = []
        for block_of_lines in raw_entries:
            out = self.parse_raw_entry(block_of_lines)
            if out is not None:
                results.append(out)
        logger.info('END Loading and parsing a file')
        return results

    def parse_raw_entry(self, block_of_lines):
        entry = self.parse_entry(block_of_lines)
        if entry is None: return
        parser = AuthorEntryParser()
        # should be integrated into parse
        name_line = entry['name_line']
        datadict = {}
        try:
            datadict = parser.parse_line(name_line)
        except Exception, inst:
            logger.warn("Skipping entry that caused exception in parsing: '%s' exception: '%s'", name_line.encode('utf8'), inst)
            return
        if datadict is None:
            # ignore issues with aliases, flourishing dates and pseudonyms
            if not( '(see: ' in name_line or ' fl ' in name_line or 'pseudonym' in
                    name_line):
                logger.warn("Skipping name that could not be parsed: '%s'", name_line.encode('utf8'))
            return
        datadict['ps'] = entry['ps']
        datadict['works'] = entry['works']
        return datadict

    def load_lines(self, fileobj):
        '''Extract entries (block of lines ) from html file. (name + work listing) from html file.
        
        @return: list of list of lines corresponding to a single author.
        '''
        dom = bs.BeautifulSoup(fileobj, convertEntities="html")
        pre = dom.find('pre')
        # pre has some <a href inside it (illegal but hey ...)
        pre = str(pre)
        pre = unicode(pre, 'utf8')
        # open('debug.txt', 'w').write(pre)
        results = []
        # entry is more than name
        current = []
        for line in pre.split('\n'):
            if line.strip() == '': # blank line separating entries
                results.append(current)
                current = []
            elif 'pre>' not in line:
                current.append(line)
        return results

    def parse_entry(self, entry_lines):
        entry = {'name_line': None, 'ps': [], 'works': []}
        if len(entry_lines) == 0:
            return None
        entry['name_line'] = entry_lines[0]
        for line in entry_lines[1:]:
            # yes you can ps;: (&ps;: Jan ORANJE)
            out = re.match('^\(&?ps;?:(.*)\)', line)
            if out:
                pses = out.group(1).split(';')
                entry['ps'] = [ ps.strip() for ps in pses ]
            else: # assume it is a work
                entry['works'].append(line.strip())
        return entry

    def load_to_db(self, fileobj):
        import pdw.model as model
        results = self.load(fileobj)
        for rec in results:
            if rec is None: continue
            p = model.Person(name=rec['name'],
                    extras={
                        'source': u'ngcoba',
                        'original': rec['fullname'],
                        }
                    )
            if rec['ps']:
                p.aka='::'.join(rec['ps'])
            if rec['bdate']:
                p.birth_date = rec['raw_bdate']
                p.birth_date_normed = rec['bdate']
#                p.birth_date_ordered = # TODO
            if rec['ddate']:
                p.death_date = rec['raw_ddate']
                p.death_date_normed = rec['ddate']
#                p.death_date_ordered = # TODO
           # if rec['sex']
            work_parser = WorkParser()
            for work_name in rec['works']:
                title, year = work_parser.parse(work_name)
                if title:
                    work = model.Work(
                            title=title,
                            date=year
                            )
                    p.works.append(work)
        model.Session.commit()
        model.Session.clear()


