import os
import re
import urllib
import logging

from swiss import Cache

from BeautifulSoup import BeautifulSoup

logger = logging.getLogger('getdata.charm')

class CharmData:
    def process_data_urls(self):
            url_base = 'http://www.charm.kcl.ac.uk/content/'
            url_info = [
                ('italian_hmv', 'green'),
                ('italian_hmv', 'main'),
                ('italian_hmv', 'suppl', 2),
                ('italian_hmv', 'zonophone'),
                ('italian_hmv', 'green'),
                ('schubert_disco', 'schubert_songs'),
                ('american', 'columbia', 12),
                ('american', 'decca', 2),
                ('american', 'vanguard'),
                ('american', 'vox', 2),
                ('american', 'westminster'),
                ('british', 'coluniss', 3),
                ('british', 'decca78_', 3),
                ('british', 'deccalp_', 6),
                ('british', 'emilp', 7),
                ('british', 'oiseaulyre'),
                ('french', 'erato', 3),
                ('french', 'pathelp', 5),
                ('french', 'polydor', 6),
                ('french', 'pre2la', 5),
                ]
            self.url_data = [] # item example: ("westminster", "http://www.charm.kcl.ac.uk/content/american/westminster.html")
            for info in url_info:
                if len(info)==3:
                    subdir, fname, num_pages = info
                    for page in range(1, num_pages + 1):
                        self.url_data.append((fname, url_base + '%s/%s%s.html' % (subdir, fname, page)))
                else:
                    subdir, fname = info
                    self.url_data.append((fname, url_base + '%s/%s.html' % (subdir, fname)))
                    
    cachedir = os.path.join('cache', 'charm')

    def __init__(self):
        self.process_data_urls()
        self.retriever = Cache(self.cachedir)

    def download(self):
        for data_name, url in self.url_data:
            logger.info('Retrieving: %s' % url)
            self.retriever.retrieve(url)

    def load_rec(self, rec):
        import pdw.model as model
        import pdw.search
        item = model.Item.query.filter_by(srcid=rec['srcid']).first()
        if item:
            #TODO sort out idempotent
            logger.warn('Duplicate record ignored %s' % rec['srcid'])
            return

        finder = pdw.search.Finder()
        title = rec['title']
        work_title = rec['work_title']
        if not title:
            logger.info('Skipping item with no title: %s' % rec)
            return
        # TODO: v. crude ...
        work = finder.work(work_title, rec['composer'])
        if work is None:
            work = model.Work(
                    title=work_title,
                    type=model.WORK_TYPES.recording,
                    )
            for name in rec['composer']:
                person = finder.person(name)
                if not person:
                    person = model.Person(name=name)
                work.persons.append(person)
        date = rec['date']
        item = model.Item(
            title=rec['title'],
            date=date,
            extras=rec['extras'],
            type=model.WORK_TYPES.recording,
            srcid=rec['srcid']
            )
        work.items.append(item)
        
    def load_into_db(self, recs):
        import pdw.model as model
        if not hasattr(self, 'count') or self.count is None:
            self.count = -1
        for rec in recs:
            self.count += 1
            if self.count % 100 == 0:
                msg = u'%s, %s' % (self.count, rec['title'])
                logger.info(msg)
            try:
                self.load_rec(rec)
                model.Session.commit()
            except Exception, inst:
                msg = '*******\n'
                msg += '%s\n%s' % (inst, rec)
                logger.error(msg)
                raise

    def find_url(self, data_name, index=None):
        '''
        Find corresponding URL for data_name
        '''
        url_pairs = []
        count = 0
        for saved_data_name, url in self.url_data:
            if not data_name or saved_data_name.startswith(data_name):
                count += 1
                if index==None or count==index:
                    url_pairs.append((saved_data_name, url))
        return url_pairs

    def load_data(self, data_name=None, index=None):
        '''
        For the specified Charm data set, parse it and load into the db.
        @data_name: (string) The data\'s html basename. If None, then all data.
        '''
        if not data_name:
            url_pairs = self.url_data
        else:
            url_pairs = self.find_url(data_name, index)
        assert url_pairs, "Could not find URL for data name: '%s'" % data_name

        #Do the loading for the matching urls
        for data_name, url in url_pairs:
            self.load_data_from_url(data_name, url)

    def load_data_from_url(self, data_name, url):
        logger.info('Loading Charm data \'%s\' (%s)' % (data_name, url))

        # Retrieve data for url
        filepath = self.retriever.filepath(url)
        fileobj = open(filepath)

        try:
            # Parse each record
            parser = CharmParser(data_name, url, fileobj)
            for rec in parser.get_parser():
                total, ok, discard = parser.get_status()
                # Load each record into db
                self.load_into_db([rec])
            logger.info('Loaded %i (of which %i are complete) records from %s' % (total, ok, url))
        finally:
            fileobj.close()
        
class CharmParser(object):
    def __init__(self, data_name, url, fileobj):
        '''
        @url:URL only needed for identifying special cases
        '''
        self._data_name = data_name
        self._url = url
        self._fileobj = fileobj
        
        self.num_total_records = 0
        self.num_complete_records = 0
        self.discarded_records = []
        
        self._parser_map = {"schubert_songs":self._parse_schubert,
                           "columbia":self._parse_gray,
#                           "green":self._parse_italian_hmv,
                           }

    def get_parser(self):
        parser = self._parser_map[self._data_name]
        return parser()

    def get_status(self):
        return self.num_total_records, self.num_complete_records, self.discarded_records
    
    def _parse_italian_hmv(self):
    #Example:
    #<h1 class="content">Italian green label catalogue</h1>
    #<h2 class="content"><a name="d0e41"></a>Band records</h2>
    #<h3 class="content"><a name="d0e45"></a>     BANDA DELLA LEGIONE RR CARABINIERI DI ROMA (CAJOLI) (Rome)
    #</h3>
    #<p class="content"><a name="250000"></a><a name="680y"></a>250000680y     19-10-09    A bocca d'Arno (Cajoli)
    #</p>
    #<p class="content"><a name="250001"></a><a name="685y"></a>250001685y     19-10-09    Marcia trionfale (Cherubini)
    #</p>
        # TODO
        pass
    
    def _parse_schubert(self):
        '''
        # record format
        # <a>ID</a>
        # <a>ID</a>
        # some id
        # <i>title</i>
        # rest of stuff
        #   (in source nicely ordered by line -- almost occassionally not and
        #   then indented ...)
        '''
        soup = BeautifulSoup(self._fileobj, convertEntities='html')
        count = -1
        for p in soup.findAll('p', 'content'):
            count += 1
            rec = { 'title': '',
                    'work_title': '',
                    'extras': {'source': 'charm.schubert'},
                    'date': None,
                    'notes': None,
                    'composer': [u'Schubert, Franz'],
                    }
            # first one is irrelevant 
            if count == 0:
                continue

            self.num_total_records += 1
            rec['title'] = p.contents[3].string
            rec['work_title'] = rec['title'].replace(' [excerpt]', '')
            # v.useful: line breaks are significant (most of the time!!!)
            # \n always at start of contents so ignore it
            ## TODO: deal with fact not all lines are like this ...
            ## Is it worth the effort?
            rest = p.contents[4].split('\n')[1:]
            indent = len(rest[0]) - len(rest[0].lstrip())
            rest = [ x.strip() for x in p.contents[4].split('\n')[1:] ]
            rec['date'] = rest[4]

            srcid = u'charm.%s::%i' % (self._data_name, count)
            
            # Not reliable
            #srcid = 'charm.%s::%s' % (self._data_name, rest[6].strip().replace(' ', ''))
            rec['srcid'] = srcid
            rec['extras']['original'] = ' '.join(rest[:4] + rest[5:])

            if rec['date'] and rec['title'] and rec['composer']:
                self.num_complete_records += 1

            yield rec

    def _parse_gray(self):
        '''
        In table form but some oddities. Every alternate column (starting with
        first) is empty.
        '''
        soup = BeautifulSoup(self._fileobj, convertEntities='html')
        results = []
        headings = []
        previous_record_srcids = set()
        table = soup.find('table', 'normal')
        def clean(td):
            if td.string is None: return None
            else: return td.string.strip()
        # for tr in table.findAll('td', # 'tableodd'):
        #        attrs={'class': ['tableodd', 'tableeven']}):
        count = -1
        for tr in table.findAll('tr'):
            count += 1
            matrix_heading_count = 1
            
            tds = tr.findAll('td')
            if len(tds) < 2: # blank tdCatalog lines ...
                continue
            # alternate cols are empty (starting at 1st)
            row = [ clean(td) for td in tds[1::2] ]
            if count == 0: # headings
                # Cope with this particular file that has no header row
                if self._url.endswith('columbia8.html'):
                    row = [u'Matrix nr', u'Date', u'Location', u'Artist (1)', u'Composer', u'Work', u'Matrix nr (part)', u'Matrix nr (part)', u'Matrix nr (part)', u'Catalogue nr (LP)', u'Catalogue nr (LP)', u'Artist (2)', u'Artist (3)', u'Notes']
                headings = []
                for heading in row:
                    if heading == 'Matrix nr (part)':
                        heading = 'Matrix nr (part %i)' % matrix_heading_count
                        matrix_heading_count += 1
                    headings.append(heading.lower())
            else:
                self.num_total_records += 1                
                rec = dict(zip(headings, row))

                try:
                    srcid = 'charm.%s::%s' % (self._data_name, rec['matrix nr (part 2)'] + rec['matrix nr (part 3)'])
                except:
                    logger.warn('Skipping record because couldn\'t make srcid. Record: %s' % row)
                    continue

                # Ignore record duplicates
                if srcid in previous_record_srcids:
                    logger.warn('Skipping record with duplicate source ID \'%s\'' % srcid)
                    continue
                previous_record_srcids.add(srcid)
                
                rec['srcid'] = srcid
                rec['work_title'] = rec['work']
                rec['title'] = rec['work']
                if rec['composer'] is not None:
                    rec['composer'] = [ rec['composer'] ]
                else:
                    rec['composer'] = []
                rec['extras'] = {
                        'source': 'charm.gray.%s' % self._data_name,
                        'original': row,
                        'label': self._data_name
                        }

                if rec['date'] and rec['title'] and rec['composer']:
                    self.num_complete_records += 1
                
                yield rec
    

if __name__ == '__main__':
    charm = CharmData()
    charm.download()

