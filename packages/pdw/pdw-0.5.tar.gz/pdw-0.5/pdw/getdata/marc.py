'''Parse marc data into a suitable form for DB.

ParserOpenLibrary uses openlibrary catalog.marc code to do basic parsing and
then converts resulting dicts into domain objects.
'''
import os
import logging
import sys
import traceback
import time

# From http://github.com/openlibrary/openlibrary/`
# Checked out and used 2009-02-28
# have to modify catalog/utils.py to not import web
import catalog.marc.fast_parse
import catalog.marc.new_parser
# Open Library code requires pymarc ...
# import pymarc

import pdw.model as model
import pdw.name

logger = logging.getLogger('pdw.getdata.marc')

class ParserOpenLibrary(object):
    parsed_srcids = set()

    def load_to_db_by_name(self, subset):
        cache_path = os.path.join('cache', 'betts', 'marc_for_rufus')
        if subset == 'all':
            fnames = os.listdir(cache_path)
        else:
            fnames = [subset]
        logger.info('Starting parsing and loading file(s): %s' % ', '.join(fnames))

        for fname in fnames:
            logger.info('===== Processing file: %s =====' % fname)
            fp = os.path.join(cache_path, fname)
            srcid_prefix = 'marc.betts.%s' % fname
            fileobj = open(fp)
            try:
                self.load_to_db(fileobj, srcid_prefix)
            finally:
                fileobj.close()        
    
    def load_to_db(self, fileobj, srcid_prefix):
        start = time.time()
        count = 0
        for rec in self.parse(fileobj, srcid_prefix):
            count += 1
            if count % 1000 == 0:
                model.Session.commit()
                model.Session.clear()
                elapsed = time.time() - start
                msg = 'Parsed and saved in db record: %i (time: %s)' % (count, elapsed)
                logger.info(msg)
        model.Session.commit()
        model.Session.clear()
    
    def parse(self, fileobj, srcid_prefix):
        '''
        @param srcid_prefix: prefix used when constructing srcids. If None do
        not create srcids.
        '''
        self._srcid_prefix = srcid_prefix
        num_records = num_parsed_records = 0
        for data, int_length in catalog.marc.fast_parse.read_file(fileobj):
            # loc used by OL internally but we don't need it
            # loc = "%s:%d:%d" % (part, pos, int_length)
            loc = None 
            try:
                num_records += 1
                # dict
                edition = catalog.marc.new_parser.read_edition(loc, data)
                item = self._dict2record(edition)
                if item:
                    num_parsed_records += 1
                    yield item
            except Exception, inst:
                logger.warn(str(inst))
                print inst
                print edition
                traceback.print_exc(file=sys.stdout)
        logger.info("Parsed success: %i/%i (%i%%)" % (num_parsed_records, num_records, int(float(num_parsed_records)/float(num_records)*100.0)))

    def clean_year(self, year):
        # replace by 9 to be conservative (i.e. make work younger)
        year = year.replace('?', '9')
        # TODO: support latin stuff like M.DCC.LIII
        chs = list(year)
        chs = filter(lambda x: x in list('0123456789'), chs)
        newyear = ''.join(chs)
        if newyear:
            return int(newyear)
        else:
            return None

    def _dict2record(self, indict):
##          {'name': u'Leighton, William Sir',
##           'personal_name': u'Leighton, William',
##           'death_date': u'1622',
##           'db_name': u'Leighton, William Sir ca. 1565-1622',
##           'birth_date': u'ca. 1565',
##           'title': u'Sir',
##           'entity_type': 'person'}

        item = model.Item()

        def seta(obj, key, attrname=None, dict2use=None, isyear=False):
            if not dict2use:
                dict2use = indict
            if not attrname:
                attrname = key
            if dict2use.has_key(key):
                val = unicode(dict2use[key])
                # cheap way to convert years to integers
                if isyear:
                    val = self.clean_year(val)
                setattr(obj, attrname, val)

        # title
        seta(item, 'title')
        # TODO: also store work_title

        # publish date
        seta(item, 'publish_date', 'date', isyear=True)

        # author
        for authord in indict.get('authors', []):
            author = model.Person(
                    )
            if authord['entity_type'] == 'person':
                # already normalized as Last, First
                name = pdw.name.parse_name(authord['personal_name'])
                seta(name, 'title', dict2use=authord)
            else: # entity type org or ...
                name = model.Name(ln=authord['name'])
            author.name = pdw.name.name_tostr(name)
            if not author.name:
                logger.info("Ignoring an author for item '%s' because name not given" % (item.title))
                model.Session.expunge(author)
                continue
            seta(author, 'birth_date', 'birth_date', dict2use=authord, isyear=True)
            seta(author, 'death_date', 'death_date', dict2use=authord, isyear=True)
            seta(author, 'entity_type', dict2use=authord)
            item.persons.append(author)

        # type / format
        physical_format = indict.get('physical_format')
        if physical_format:
            physical_format = physical_format.lower()
            if 'videorecording' in physical_format:
                # discard video recordings
                logger.info("Ignoring item '%s' because it is a video recording (format: '%s')" % (item.title, physical_format))
                model.Session.expunge(item)
                return None

            if 'sound recording' in physical_format:
                item.type = model.WORK_TYPES.recording

        # srcid
        def get_srcid():
            if not self._srcid_prefix:
                return None
            id_elements = []
            for id_num_str in indict.get('lccn', []):
                id_elements.append(u"LCCN%s" % str(int(id_num_str)))
            for id_num_str in indict.get('isbn_10', []):
                id_elements.append(u"ISBN%s" % id_num_str)
            for id_num_str in indict.get('isbn_13', []):
                id_elements.append(u"ISBN%s" % id_num_str)
            id = '.'.join(id_elements)
            if id:
                return u'%s::%s' % (self._srcid_prefix, id)
            else:
                logger.debug("Item '%s' has no srcid generated." % item.title)

        srcid = get_srcid()
        # check srcid is unique (to this parse anyway)
        if srcid:
            if srcid in self.parsed_srcids:
                logger.info("Ignoring item '%s' with duplicate srcid '%s'" % (item.title, srcid))
                model.Session.expunge(item)
                return None
            item.srcid = srcid
            self.parsed_srcids.add(srcid)

        # original record
        item.marc_source = indict

        return item




# ===========================================================
# PDW from scratch MARC Parser

import pymarc
ID = '001'
AUTHOR = '100'
TITLE = '130'
FULLTITLE = '245'
PUBINFO = '260'

def _(instr):
    # pymarc.marc8_to_unicode(
    return instr.decode('utf8')

# TODO: 2009-03-05 Fix this up ...
class ParserPdw(object):
    def parse(self, fileobj):
        reader = pymarc.reader.MARCReader(fileobj)
        for marc in reader:
            id = marc[ID].data
            title = self.title(marc)
            pubyear = self.pubyear(marc)
            authors, editors = self.authors(marc)
            record = model.Item(
                    title=title,
                    date=pubyear
                    )
            record.persons = authors
            # record.editors = editors
            record.marc = marc
            yield record

    def authors(self, record):
        '''Main author field is 100. However this seems usually to contain only
        one value. Need to check 700 as well.

        Also need to distinguish editors from authors. Appears one can tell
        this by the fact that if authors at least one of them listed in field
        100
        
        author date in d field: rec[AUTHOR]['d']
        '''
        # do it by hand rather than use author = marc.author()
        def extract_persons(field_id):
            authors = []
            for field in record.get_fields(field_id):
                fn = self.subfield(field, 'a')
                dates = self.subfield(field, 'd')
                birth, death = self.clean_author_dates(dates)
                author = model.Person(
                        name=fn,
                        birth_date=birth,
                        death_date=death)
                authors.append(author)
            return authors

        authors = extract_persons(AUTHOR)
        extras = extract_persons('700')
        editors = []
        
        if authors:
            authors = authors + extras
        else:
            # do not bother with editors for time being
            # editors = extras
            authors = extras
        return authors, editors
    
    def clean_author_dates(self, dates_str):
        if not dates_str:
            return (None, None)
        out = dates_str.split('-')
        # never has len 0
        if len(out) == 1: # be conservative and assume it is birth date
            birth = out[0]
            death = ''
        else:
            birth, death = out
        birth = self.clean_year(birth)
        death = self.clean_year(death)
        return birth, death
    
    def title(self, rec):
        # use built-in support
        return _(rec.title())
        
        # first try 100
        # title = fields(TITLE, 'a')
        # if not title:
        #    title = fields(rec, FULLTITLE, 'a') + fields(rec, FULLTITLE, 'b')
        # return title

    def clean_year(self, year):
        # replace by 9 to be conservative (i.e. make work younger)
        year = year.replace('?', '9')
        # TODO: support latin stuff like M.DCC.LIII
        chs = list(year)
        chs = filter(lambda x: x in list('0123456789'), chs)
        newyear = ''.join(chs)
        if newyear:
            return int(newyear)
        else:
            return None

    def pubyear(self, rec):
        # pubdate = rec[PUBINFO]['c']
        # pubdate2 = fields(rec, TITLE, 'f')
        # TODO: can have multiple 'c' entries many of which are not dates ...
        year = rec.pubyear()
        if year:
            out = self.clean_year(year)
            # TODO: make this a debug ...
            if not out:
                msg = 'Unable to extract pubyear: %s\n%s' % (year, rec)
                logger.warn(msg)
            return out
        else:
            return None

    def subfield(self, field, subfield_id=None):
        if field:
            if subfield_id is None:
                return _(field.data)
            try:
                data = field[subfield_id]
                return _(data)
            except:
                return None
        return None

    def fields(self, record, field_id, subfield_id=None):
        results = []
        for field in record.get_fields(field_id):
            data = self.subfields(field, subfield_id)
            if data:
                results.append(data)
        return results


