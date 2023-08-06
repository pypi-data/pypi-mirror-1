# http://openlibrary.org/dev/docs/api
import datetime
import simplejson
import urllib

import dateutil.parser

from pdw.name import Name, FirstLast, parse_name, name_tostr
import pdw.pd
import pdw.model as model

class Loader(object):
    '''Load from OL json dumps'''

    def load_authors(self, fileobj):
        for xx in self.load_to_db(fileobj, objtype='person'):
            yield xx

    def load_editions(self, fileobj):
        for xx in self.load_to_db(fileobj, objtype='item'):
            yield xx

    def load_to_db(self, fileobj, objtype='person'):
        '''Load from standard OL json dumps.
        
        @param fileobj: fileobj of data dump
        @param objtype: person (for authors) and item (for editions)
        '''
        for line in fileobj:
            record = simplejson.loads(line)
            if objtype == 'person':
                modelobj = self.record2person(record)
            elif objtype == 'item':
                modelobj = self.record2item(record)
            else:
                raise ValueError('Unknown objtype: %s' % objtype)
            yield modelobj

    def srcid(self, key):
        srcid = u'ol::%s' % key
        return srcid

    def record2person(self, record):
        srcid = self.srcid(record['key'])
        # should we check if it exists?
        # model.Person.query.filter_by(srcid=srcid)
        name = pdw.name.normalize(record.get('name', None))
        person = model.Person(name=name,
                srcid=srcid,
                birth_date=record.get('birth_date', None),
                death_date=record.get('death_date', None)
                )
        return person

    def record2item(self, record):
        srcid =self.srcid(record['key'])
        item = model.Item(title=record.get('title', None),
           date=record.get('publish_date', None),
           )
        # TODO: ? physical_format, number_of_pages
        for field in [ 'publishers', 'isbn_13', 'isbn_10' ]:
            if field in record:
                item.extras[field] = record[field]
        if 'languages' in record:
            # languages = [ {"key": "/l/eng"} ]
            val = [ x['key'].split('/')[-1]  for x in record['languages'] ]
        item.extras['languages'] = val
        for author in record['authors']:
            authorid = self.srcid(author['key'])
            person = model.Person.query.filter_by(srcid=authorid).one()
            item.persons.append(person)
        return item


class OLQuery(object):
    baseurl = 'http://openlibrary.org/api/'

    def search_author(self, name):
        query = {
            'type':'/type/author',
            'name':''
            }
        query['name'] = name
        fullurl = self.baseurl + 'things?' + urllib.urlencode({'query':simplejson.dumps(query)})
        uo = urllib.urlopen(fullurl)
        return_data = simplejson.loads(uo.read())
        if 'result' in return_data:
            return return_data['result']
        else:
            return None

    def search_book(self, title=''):
        # normalize (remove trailing articles)
        if title.endswith(',A'): title = title[:-2]
        if title.endswith(',The'): title = title[:-4]
        # cannot deal with punctuation ...
        title = title.replace('!', '') 
        title = title.replace('?', '') 
        query = { 'query': title }
        fullurl = self.baseurl + 'search?' + urllib.urlencode({'q':simplejson.dumps(query)})
        uo = urllib.urlopen(fullurl)
        return_data = simplejson.loads(uo.read())
        if 'result' in return_data:
            return return_data['result']
        else:
            return None

    def object_search_book(self, title='', isbn_13=''):
        '''Search for a book by title or isbn using object search.

        Only works with isbn13 from US in general.
        E.g. isbn13 = '9780747591061' (JK Rowling stuff) does not work

        Problem with using object ('things') query is that it seems to
        require the title to be exactly right.

        For example: Spot of Bother won't match but A Spot of Bother will.
        '''
        # other options
        #    "authors": "\/a\/OL18319A",
        #    "sort": "key",
        #    "limit": 5
        query = {
            'type':'/type/edition',
            'limit': 10
            }
        if isbn_13:
            query['isbn_13'] = isbn_13
        if title:
            # normalize (remove trailing articles)
            if title.endswith(',A'): title = title[:-2]
            if title.endswith(',The'): title = title[:-4]
            print title
            query['title'] = title
        fullurl = self.baseurl + 'things?' + urllib.urlencode({'query':simplejson.dumps(query)})
        uo = urllib.urlopen(fullurl)
        return_data = simplejson.loads(uo.read())
        # pick first result
        if 'result' in return_data:
            return return_data['result']
        else:
            return None

    def get_object(self, id):
        fullurl = self.baseurl + 'get?key=%s' % id
        # print fullurl
        uo = urllib.urlopen(fullurl)
        return_data = simplejson.loads(uo.read())
        # print return_data
        if return_data['status'] == u'ok':
            return return_data['result']
        else:
            return None

    def by_work(self, work):
        '''Determine PD status of a work.

        @param work: a pdw.model.Work object.
        '''
        # bit of a hack for handling odd stuff ...
        # e.g. We Need to Talk About Kevin:Five Star Paperback S.
        title = work.title.split(':')[0]
        editions = self.search_book(title=title)
        if not editions:
            return (False, None, 'No edition')
        # OL wants them in 
        names = [ name_tostr(parse_name(p.name), parser_class=FirstLast) for p in work.persons ]
        # do max of 10
        for e in editions[:10]:
            edobj = self.get_object(e)
            # print 'Processing', edobj
            authors = [ self.get_object(a['key']) for a in
                    edobj.get('authors', []) ]
            out_names = [ a['name'] for a in authors ]
            names.sort()
            out_names.sort()
            if names == out_names:
                # print 'Match'
                for a in authors:
                    if not self.person_is_pd(a):
                        return (False, e, '')
                return (True, e, '')
        return (False, None, '')

    # query by title, then by author and then get death date (if exists)
    def person_is_pd(self, person):
        if 'death_date' in person:
            d = dateutil.parser.parse(person['death_date'],
                    default=datetime.datetime(2008,01,01))
            return pdw.pd.out_of_authorial_copyright(d)
        else:
            return False


if __name__ == '__main__':
    import optparse
    usage = '''%prog {action}

    title {title-string}
    byid {id}
    '''
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()
    if not args:
        parser.print_help()

    action = args[0]
    olq = OLQuery()
    if action == 'title':
        title = args[1]
        print title
        print olq.search_book(title)
    elif action == 'byid':
        oid = args[1]
        out = olq.get_object(oid)
        # print out
        print simplejson.dumps(out)

