"""
Parse html pages downloaded from British Library Sound Archive Catalogue to
extract information on recordings and insert this into the pdw database.
"""
import os
import datetime
from HTMLParser import HTMLParser
import re
from htmlentitydefs import name2codepoint

debug = True

# htmldecode is taken from
# http://zesty.ca/python/scrape.py (Ka-Ping Yee)

# This pattern matches a character entity reference (a decimal numeric
# references, a hexadecimal numeric reference, or a named reference).
charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')

specialEntities = [ 'amp', 'lt', 'gt' ]
specialEntitiesInvert = { 'amp' : '&', 'lt' : '<', 'gtgtgt' : '>' }
def specialencode(entity):
    out = '[[%s]]' % (3 * entity)
    return out

def specialdecode(_str):
    try:
        out = _str
        for entity in specialEntities:
            out = out.replace(3*entity, chr(name2codepoint[entity])) 
        return out
    except:
        print _str
        raise

def htmldecode(text):
    """Decode HTML entities in the given text."""
    if type(text) is unicode:
        uchr = unichr
    else:
        uchr = lambda value: value > 255 and unichr(value) or chr(value)
    def entitydecode(match, uchr=uchr):
        entity = match.group(1)
        if entity.startswith('#x'):
            return uchr(int(entity[2:], 16))
        elif entity.startswith('#'):
            return uchr(int(entity[1:]))
        elif entity in name2codepoint:
            # inserted by rgrp do deal with problematic substitutions
            if entity in specialEntities:
                return specialencode(entity)
            return uchr(name2codepoint[entity])
        else:
            return match.group(0)
    return charrefpat.sub(entitydecode, text)

def tou(instr):
    return instr.decode('utf8', 'ignore') 

class SoundArchiveHtmlParser(HTMLParser):
    
    _acceptClassType = [ 'viewmarctags', 'holdingslist' ]

    def reset(self):
        HTMLParser.reset(self)
        self.recording_details = None
        self.recording_details = {}
        self._printState = False
        self._tagStack = []
        self._itemsArray = []
        self._printState = False

    def feed(self, data):
        self.reset()
        html = unicode(data)
        html = self.fix_bad_html(data)
        # fix entity references in page rather than mess around elsewhere
        # to deal with &amp; and other problematic ones we block them in
        # htmldecode and then resub below
        html = htmldecode(html)
        HTMLParser.feed(self, html)
        # resub
        self._itemsArray = [ specialdecode(xx) for xx in self._itemsArray ]
        self.get_work_details()

    def fix_bad_html(self, html):
        html = html.replace('<! START CHANGE', '<!-- START CHANGE')
        html = html.replace('<! ENDCHANGE', '<!-- ENDCHANGE')
        return html
    
    def handle_starttag(self, tag, attrs):
        dictattrs = dict(attrs)
        if dictattrs.get('class', 'noclasstag') not in self._acceptClassType:
            pass
        else:
            self._printState = True
            self._tagStack.append(tag)

    def handle_data(self, text):
        cleantext = text.strip()
        if self._printState and len(cleantext) > 0:
            self._itemsArray.append(cleantext)

    def handle_entityref(self, name):
        msg = 'Have entity ref: %s left after doing htmldecode' % name
        raise Exception(msg)

    def handle_charref(self, name):
        msg = 'Have entity ref: %s left after doing htmldecode' % name
        raise Exception(msg)

    def handle_endtag(self, tag):
        if len(self._tagStack) == 0 or self._tagStack != self._tagStack[-1]:
            return
        tag = self._tagStack.pop()
        self._printState = False

    def get_work_details(self):
        """Get recording details as extracted from html in dictionary form.
        Call feed first then this method.

        Notes on extraction:
            * we do not extract data in html from bibinfo section specfically
              that after
              
              <!-- Print the title, if one exists -->
              <strong>title</strong>
              <!-- Print the author, if one exists -->
              .... something
              
              because:
                a) title always duplicates what is available elsewhere
                b) author info seems inaccurate (it always seems to be one of
                the performers)
        """
        fieldNames = [ 'performer',
                       'recording_location',
                       'recording_date',
                       'item_notes',
                       ]
        details = {}
        details['title'] = tou(self._itemsArray[1])
        details['performer'] = []
        # now start on rest of tags
        saveNext = False
        fieldName = None
        for item in self._itemsArray:
            tmp = item.lower()
            tmp = tmp.replace(' ', '_')
            tmp = tmp.replace(':', '')
            if tmp in fieldNames:
                fieldName = tmp
                saveNext = True
                continue
            if saveNext:
                if fieldName == 'performer':
                    tcurrent = details['performer']
                    tcurrent.append(tou(item))
                    details['performer'] = tcurrent
                else:
                    details[fieldName] = tou(item)
            saveNext = False
        self.recording_details = details

import pdw.model as model
class PerformanceWriter(object):
    """Write recordings to the db
    
    TODO: deal with empty titles properly
    TODO: deal with empty author
    """

    def get_recording(self, recording):
        """Create a Performance db object (and any associated other items) given
        recording details given by recording.
        """
        longTitle = recording['title']
        title, authorNames = self.process_long_title(longTitle)
        work = self.get_work(title, authorNames)
        rec = model.Performance(work=work)
        # use simple string as have lots of dates like 1900.ca or 1900-1905
        # year, month, day = recording['recording_date'].split('.')
        # _date = datetime.date(int(year), int(month), int(day))
        if recording.has_key('recording_date'):
            rec.recordingDate = recording['recording_date']
        # todo: item notes etc
        for perf in recording['performer']:
            perf = perf or u'UNKNOWN' 
            art = self.get_artist(perf)
            rec.performers.append(art)
        rec.notes = self.get_notes(recording)
        model.Session.commit()
        return rec

    def get_notes(self, recording):
        out = u''
        for key in ['recording_location', 'item_notes']:
            if recording.has_key(key):
                out += '%s: %s; ' % (key, recording[key])
        return out

    def process_long_title(self, longTitle):
        # title often given as title/Author (but not always) need to deal with
        # 1. no /
        # 2. multiple /
        # e.g. He Loves Me, He Loves Me Not/Stuart/boyd 
        # this is actually  Leslie Stuart, with lyrics by Ernest Boyd-Jones
        # (for show Florodora)
        # see http://www.staff.ncl.ac.uk/fraser.charlton/florosyn.html
        # 3. Alabama dream./
        unknownAuthorName = u'UNKNOWN'
        title = longTitle
        authorNames = []
        splitTitle = longTitle.split('/')
        numitems = len(splitTitle)
        if numitems == 1:
            authorNames = [unknownAuthorName]
        elif numitems > 1:
            title = splitTitle[0].strip()
            authorNames = splitTitle[1:]
        else:
            msg = 'Something very wrong on split of longTitle: %s' % longTitle
            raise ValueError(msg)
        title = title or u'UNKNOWN WORK'
        for ii in range(len(authorNames)):
            tmp = authorNames[ii].strip()
            if not tmp:
                tmp = unknownAuthorName
            authorNames[ii] = tmp
        return (title, authorNames) 

    def get_work(self, title, authorNames):
        """Create a Work in the db and return the resulting Work sqlobject.
        """
        # TODO: more rigorous checking (use author ...)
        title = title
        existingWork = self.get_existing_work(title, authorNames)
        if existingWork is not None:
            return existingWork
        work = self.create_work(title, authorNames)
        return work
    
    def get_existing_work(self, title, authorNames):
        # TODO: more rigorous checking (use author ...)
        out = model.Work.query.filter_by(title = title).all()
        work = None
        if len(out) == 0:
            return None
        work = out[0]
        if len(out) > 1:
            msg = 'WARNING: Multiple works with title = %s. ' % title
            msg += 'Will use first work in list: %s' % work
            # TODO: use logger
            print msg
        return work

    def create_work(self, title, authorNames):
        if not title:  # None or ''
            raise ValueError('Cannot create a work with blank title')
        work = model.Work(title=title)
        for authorName in authorNames:
            artist = self.get_artist(authorName)
            work.creators.append(artist)
        return work
    
    def get_artist(self, fullName):
        fullName = fullName
        existingArtist = self.get_existing_artist(fullName)
        if existingArtist is None:
            artist = self.create_artist(fullName)
            return artist
        return existingArtist

    def get_existing_artist(self, fullName):
        out = model.Artist.query.filter_by(full_name = fullName).all()
        if len(out) == 0:
            return None
        artist = out[0]
        if len(out) > 1:
            msg = 'WARNING: Multiple artists with last name = %s. ' % fullName
            msg += 'Will use first artist in list: %s' %  artist
            # TODO: use logger
            print msg
        return artist

    def create_artist(self, fullName):
        if not fullName:
            msg = 'Cannot create and artist with blank name (use UNKNOWN)'
            raise ValueError(msg)
        artist = model.Artist(fullName=fullName)
        return artist

import pdw
cachedir = pdw.conf().get('DEFAULT', 'cache')
def parse(handler, filter):
    """Extract recording details from all cached html and process using handler
    @filter: a function applied to each file name to determine whether to
    process it
    """
    parser = SoundArchiveHtmlParser()
    for ff in os.listdir(cachedir):
        if filter(ff):
            filePath = os.path.join(cachedir, ff)
            if debug:
                print filePath
            html = file(filePath, 'r').read()
            parser.feed(html)
            handler(parser.recording_details)

