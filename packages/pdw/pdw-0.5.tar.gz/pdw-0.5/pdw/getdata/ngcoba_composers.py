import re
import dateutil.parser
import datetime

from pdw.pd import *

class ComposerFileParser(object):
    """Parse composers.txt received from kingkong.demon.co.uk.

    TODO:
    
        * deal with dates such as c1760 (do we create an extra item named
          notes?)
    """

    month_to_int = {
            'jan' : 1,
            'feb' : 2,
            'mar' : 3,
            'apr' : 4,
            'may' : 5,
            'jun' : 6,
            'jul' : 7,
            'aug' : 8,
            'sep' : 9,
            'oct' : 10,
            'nov' : 11,
            'dec' : 12
            }
    
    def __init__(self):
        # yes Fr is a title (used for Monteverdi ...)
        self.line_regex = """
        (?:(?P<title>Graf|King|Lady|Mrs|Prof|Rev|Sir|Fr),?)?
        (?P<fullname> [^,]+ ),
        (?P<extra> (?:(?:(?!\s\*) [^,]+) , )* )
        (?:\s\*\s (?P<bdate> [^,]+)),
        (?:\s\+\s (?P<ddate> .+))
        """
        self.line_pat = re.compile(self.line_regex, re.VERBOSE)
    
    def parse_line(self, line):
        sections = self._sections(line) 
        if sections is None: # no match
            return None
        result = dict(sections)
        result['errors'] = []
        lname, fname, alias = self._parse_name(sections['fullname'])
        bdate, errors1 = self.parse_date(sections['raw_bdate'])
        ddate, errors2 = self.parse_date(sections['raw_ddate'])
        result['lname'] = lname
        result['fname'] = fname
        result['bdate'] = bdate
        result['ddate'] = ddate
        result['errors'] += errors1 + errors2
        aliases = []
        if alias != '':
            aliases.append(alias)
        # TODO: parse alias stuff properly
        if result['extra'] != '':
            aliases.append(result['extra'])
            # del result['extra']
        result['aliases'] = aliases
        return result

    def _sections(self, line):
        mat = self.line_pat.match(line)
        if mat is None:
            return None
        sections = {}
        sections['fullname'] = mat.group('fullname')
        sections['raw_bdate'] = mat.group('bdate')
        sections['raw_ddate'] = mat.group('ddate')
        sections['extra'] = mat.group('extra')
        return sections

    def _parse_name(self, fullname):
        # annoyingly sometimes get aliases put in brackets at end
        regex = '(.*[^)])(?: \(([^)]+)\))?$'
        out = re.findall(regex, fullname)[0]
        names = out[0].split()
        alias = out[1].strip()
        lname = names[-1]
        fname = ' '.join(names[:-1])
        return (lname, fname, alias)
    
    def parse_date(self, datestr):
        datestr = datestr.strip()
        if datestr.startswith('?'):
            return None, []
        try:
            datestr = self.extract_date_info(datestr)
            if datestr.startswith('c'): # ignore circa stuff
                datestr = datestr[1:]
            out = dateutil.parser.parse(datestr, default=datetime.datetime(1,1,1))
            return datetime.date(out.year, out.month, out.day), []
        except Exception, inst:
            return None, [ str(inst) ]

    def extract_date_info(self, date):
        # can have years with less than 4 digits
        regex = '(\w?\d{3,4})(?:\s+(\w+)(?:\s(\d+))?)?'
        vals = re.findall(regex, date)[0]
        result = vals[0]
        if vals[1] != '':
            month = self.month_to_int[vals[1].lower()]
            result += '-%s' % month
        if vals[2] != '':
            result += '-%s' % vals[2]
        return result


def parse_file(filepath):
    results = []
    ff = file(filepath)
    parser = ComposerFileParser()
    count = 0
    error = False
    for line in ff:
        try:
            out = parser.parse_line(line)
            results.append(out)
        except Exception, inst:
            print 'ERROR: ', count, inst, line
        count += 1
    return results

def analyse(item):
    ddate = item['ddate']
    if ddate is None:
        return CopyrightStatus.UNKNOWN
    if out_of_authorial_copyright(ddate):
        return CopyrightStatus.OUT
    else:
        return CopyrightStatus.IN


if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv) == 2:
        filepath = os.path.abspath(sys.argv[1])
        parse_file(filepath)
    else:
        print 'Please provide path to composers.txt'

