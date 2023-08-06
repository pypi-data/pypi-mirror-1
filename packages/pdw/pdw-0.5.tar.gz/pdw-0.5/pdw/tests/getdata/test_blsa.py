# 2009-02-11: this module is currently deprecated
# Needs updating to follow new FRBR model and to not use unittest
import unittest
import os
import pprint

import pdw
import pdw.getdata.blsa
import pdw.model as model

cachedir = pdw.conf().get('DEFAULT', 'cache')

def rebuild_db():
    model.metadata.drop_all(bind=model.Session.bind)
    model.metadata.create_all(bind=model.Session.bind)

__test__ = False

class SoundArchiveHtmlParserTest(unittest.TestCase):

    expected = { 'title' : u'Faust (Act 4)/Gounod',
                 'performer' : [ u'Unnamed Male Chorus',
                                 u'unidentified orchestra',
                                 ],
                 'recording_date' : '1900.07.14',
                 'recording_location' : u'Milan',
                 'item_notes' : u'Matrix No: (9)29(a) Orig Cat No: 54504',
                }

    def setUp(self):
        rebuild_db()
        filePath = os.path.join(cachedir, 'blsa', '1900_1.html')
        self.handler = pdw.getdata.blsa.SoundArchiveHtmlParser()
        html = file(filePath).read()
        self.handler.feed(html)

    def test1(self):
        out = self.handler.recording_details
        self.assertEqual(self.expected, out)

# test with a record with different layout
class SoundArchiveHtmlParserTest2(unittest.TestCase):
    expected = { 'performer': [u'unidentified (military band)'],
                 'item_notes': u'Dubbed from an unidentified 78 rpm disc (awaiting further identification)',
                 'recording_date': '1900 ca.',
                 'title': u'[unidentified tune]'
                 }

    def setUp(self):
        filePath = os.path.join(cachedir, 'blsa', '1900_10.html')
        self.handler = pdw.getdata.blsa.SoundArchiveHtmlParser()
        html = file(filePath).read()
        self.handler.feed(html)

    def test1(self):
        out = self.handler.recording_details
        self.assertEqual(self.expected, out)


class PutPerformanceInDbTest1(unittest.TestCase):

    writer = pdw.getdata.blsa.PerformanceWriter()
    title = u'Faust'
    fn = u'nobody'

    def test_process_long_title(self):
        in1 = u'Faust (Act 4)/Gounod'
        exp1 = (u'Faust (Act 4)', [u'Gounod'])
        out1 =self.writer.process_long_title(in1)
        self.assertEqual(exp1, out1)

    def test_process_long_title2(self):
        in1 = u'Mottoes on the wall'
        exp1 = (u'Mottoes on the wall', [u'UNKNOWN'])
        out1 =self.writer.process_long_title(in1)
        self.assertEqual(exp1, out1)

    def test_process_long_title3(self):
        in1 = u'He Loves Me, He Loves Me Not/Stuart/boyd'
        exp1 = (u'He Loves Me, He Loves Me Not', [u'Stuart', u'boyd'])
        out1 =self.writer.process_long_title(in1)
        self.assertEqual(exp1, out1)

    def test_process_long_title4(self):
        in1 = u'Alabama dream./'
        exp1 = (u'Alabama dream.', [u'UNKNOWN'])
        out1 =self.writer.process_long_title(in1)
        self.assertEqual(exp1, out1)

    def test_process_long_title5(self):
        in1 = u''
        exp1 = (u'UNKNOWN WORK', [u'UNKNOWN'])
        out1 =self.writer.process_long_title(in1)
        self.assertEqual(exp1, out1)

    def test_get_existing_artist(self):
        existing = self.writer.get_existing_artist(self.fn)
        self.assertEqual(existing, None)

    def test_get_artist(self):
        artist = self.writer.get_artist(self.fn)
        self.assertEqual(self.fn, artist.fullName)
        # model.Artist.delete(artist.id)
    
    def test_get_existing_work(self):
        existing = self.writer.get_existing_work(self.title, [self.fn])
        self.assertEqual(existing, None)

    def test_get_work(self):
        work = self.writer.get_work(self.title, [self.fn])
        self.assertEqual(self.title, work.title)
        art = work.creators[0]
        # model.Work.delete(work.id)
        # model.Artist.delete(art.id)

class PutPerformanceInDbTest2(unittest.TestCase):
    recording = {'title' : u'Faust (Act 4)/Gounod',
                 'performer' : [ u'Unnamed Male Chorus',
                                 u'unidentified orchestra',
                                 ],
                 'recording_date' : '1900.07.14',
                 'recording_location' : u'Milan',
                 'item_notes' : u'Matrix No: (9)29(a) Orig Cat No: 54504',
                }
    
    writer = pdw.getdata.blsa.PerformanceWriter()

    def setUp(self):
        # extreme measures: rebuild the db before every test
        rebuild_db()
        self.rec = self.writer.get_recording(self.recording)
        self.work = self.rec.work
        self.creator = self.work.creators[0]
        self.performers = self.rec.performers
        self.expTitle = u'Faust (Act 4)'
        self.expAuthorName = u'Gounod'
        self.expNotes = u'recording_location: Milan; item_notes: Matrix No: (9)29(a) Orig Cat No: 54504; '

    def tearDown(self):
        # now we rebuild_db this is not necessary
        pass
        # model.Performance.delete(self.rec.id)
        # for perf in self.performers:
        #     model.Artist.delete(perf.id)
        # model.Artist.delete(self.creator.id)
        # model.Work.delete(self.work.id)

    def test1(self):
        self.assertEqual(self.expNotes, self.rec.notes)
        self.assertEqual(self.expAuthorName, self.creator.fullName)
        self.assertEqual(self.expTitle, self.work.title)

    def test_get_notes(self):
        out = self.writer.get_notes(self.recording)
        self.assertEqual(self.expNotes, out)

class PutPerformanceInDbTest3(unittest.TestCase):
    # 1900_10.html (messed around)
    recording = {'performer': [u'unidentified (military band)'],
                 'item_notes': u'Dubbed from an unidentified 78 rpm disc (awaiting further identification)',
                 'recording_date': '1900 ca.',
                 'title': u'[unidentified tune]'
                 }
    
    writer = pdw.getdata.blsa.PerformanceWriter()

    def setUp(self):
        # extreme measures: rebuild the db before every test
        rebuild_db()
        self.rec = self.writer.get_recording(self.recording)
        self.work = self.rec.work
        self.creator = self.work.creators[0]
        self.performers = self.rec.performers

    def test1(self):
        # expectedNotes = self.recording['items_notes']
        self.assertEqual('UNKNOWN', self.creator.fullName)
        self.assertEqual(self.recording['title'], self.work.title)

# Z make sure it runs last
class ZParseTest2(unittest.TestCase):

    def setUp(self):
        # extreme measures: rebuild the db before every test
        rebuild_db()

    def test1(self):
        writer = pdw.getdata.blsa.PerformanceWriter()
        def filter(filename):
            return filename.startswith('1900_')
        pdw.getdata.blsa.parse(writer.get_recording, filter)
        numrecs = model.Performance.query.count()
        self.assertEqual(136, numrecs)

