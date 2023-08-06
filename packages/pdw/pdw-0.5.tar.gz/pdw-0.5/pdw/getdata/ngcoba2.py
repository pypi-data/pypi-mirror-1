import os
import re
import logging

from pdw.name import name_tostr
from pdw.getdata.ngcoba import AuthorEntryParser
from pdw.getdata.ngcoba import NameParser
from pdw.getdata.ngcoba import OurDateParser
from pdw.getdata.ngcoba import WorkParser

logger = logging.getLogger('getdata.ngcoba2')

# for loading and parsing ngcoba2 data
class Loader(object):
    
    isentry = re.compile('^\\w')

    # loads and parses a file
    def load(self, fileobj):
        logger.info('START Loading and parsing a file')
        parsed_entries = []
        srcids = set()
        is_duplicate_srcids = False
        num_entries = 0
        cont = True
        while cont:
            raw_entry = self.load_entry(fileobj)
            if raw_entry:
                num_entries += 1
                parsed_entry = self.parse_raw_entry(raw_entry)
                if parsed_entry is not None:
                    parsed_entries.append(parsed_entry)
                    srcid = parsed_entry['authorcode']
                    if srcid in srcids and srcid != None:
                        logger.error("Duplicate srcid '%s'", srcid)
                        is_duplicate_srcids = True
                    srcids.add(srcid)
            else:
                # EOF
                cont = False
        logger.info('%i/%i entries parsed', len(parsed_entries), num_entries)
        if is_duplicate_srcids:
            assert 0, 'Duplicate srcids'
        logger.info('END Loading and parsing a file')
        return parsed_entries

    def parse_raw_entry(self, block_of_lines):
        # Split raw entry into author, works etc.
        entry = self.parse_entry(block_of_lines) 
        if entry is None:
            return

        # Parse author line
        author_parser = AuthorEntryParser()
        name_line = entry['name_line']
        datadict = {}
        try:
            datadict = author_parser.parse_line(name_line)
        except Exception, inst:
            logger.warn("Skipping entry that caused exception in parsing: '%s' exception: '%s'", name_line.encode('utf8'), inst)
            return
        if datadict is None:
            # ignore issues with aliases, flourishing dates and pseudonyms
            if not( '(see: ' in name_line or ' fl ' in name_line or 'pseudonym' in
                    name_line):
                logger.warn("Skipping name that could not be parsed: '%s'", name_line.encode('utf8'))
            return
        
        # Also return pseudonymn and works
        datadict['ps'] = entry['ps']
        datadict['works'] = entry['works']
        
        return datadict

    def load_entry(self, fileobj):
        '''Loads one entry (block of lines) from file.
        Each entry is one author and a list of works.
        
        @return: list of lines for this entry. If no more entries, returns None
        '''
        entry = []
        cont = True
        while cont:
            line = unicode(fileobj.readline(), 'utf8', errors='replace')
            if line.strip():
                entry.append(line.strip())
            elif line == '':
                # EOF
                cont = False
                if not entry:
                    entry = None
            else:
                if entry:
                    # blank line indicates end of entry
                    cont = False
                # else blank line is before an entry
        return entry

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
        logger.info('START load_to_db')        
        results = self.load(fileobj)
        logger.info('Saving to database')
        count = 0
        for rec in results:
            if rec is None: continue
            p = model.Person(name=rec['name'],
                    extras={
                        'original': rec['fullname'],
                        }
                    )
            if rec['ps']:
                p.aka='::'.join(rec['ps'])
            if rec['bdate']:
                p.birth_date = rec['bdate']
            if rec['ddate']:
                p.death_date = rec['ddate']
            if 'authorcode' in rec and rec['authorcode']:
                p.srcid = "ngcoba::%s" % rec['authorcode']
            work_parser = WorkParser()
            for work_name in rec['works']:
                title, year = work_parser.parse(work_name)
                if title:
                    work = model.Work(
                            title=title,
                            date=year
                            )
                    p.works.append(work)
            count += 1
            if count % 1000 == 0:
                logger.info('Current record: %i', count)
                model.Session.commit()
                model.Session.clear()
        model.Session.commit()
        model.Session.clear()
        logger.info('END load_to_db')


