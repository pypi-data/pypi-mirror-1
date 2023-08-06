import os
import time

try:
    import pdw.getdata.mb
    import pdw.getdata.mb2dm as mb2dm
except:
    __test__ = False


class TestMusicBrainzLoader:
    __test__ = False

    @classmethod
    def setup_class(self):
        self.loader = mb2dm.MusicBrainzLoader()
        # twist and shout by the Beatles
        self.twist_and_shout = pdw.getdata.mb.get_track(
                u'http://musicbrainz.org/track/735027a3-d183-42a0-a691-7be6c166df2f')
        self.beethoven_violin = pdw.getdata.mb.get_track(
                u'http://musicbrainz.org/track/bb72afd4-4189-4243-b530-34d471970745')
        # two tracks by same artist
        self.pixinguinha = pdw.getdata.mb.get_track(
                u'http://musicbrainz.org/track/9ab4e0bc-edfa-4218-8c74-be79f31a7ef1')
        self.loader.load_track(self.twist_and_shout, None)
        # do not make more than a call a second
        time.sleep(1)
        self.loader.load_track(self.beethoven_violin, None)
        time.sleep(1)
        self.loader.load_track(self.pixinguinha, None)
        time.sleep(1)
        # this calls commit ...
        self.loader.execute()

    @classmethod
    def teardown_class(self):
        mb2dm.model.metadata.drop_all(bind=mb2dm.model.Session.bind)

    def test_1(self):
        source = u'mb::%s' % u'http://musicbrainz.org/track/6b67ab11-8254-44d9-b461-de60b50aa6b5'
        out = mb2dm.model.Work.query.filter_by(source=source).first()
        out.title == u'Oh How That German Could Love!'
        assert out.creators[0].full_name == u'Irving Berlin'
        perf = out.performances[0]
        from datetime import date
        assert perf.performance_date == date(1910, 1, 1)
        assert perf.performers[0].full_name == u'Irving Berlin'

    def test_twist_and_shout(self):
        source = self.loader._mb_source(self.twist_and_shout.id)
        out = mb2dm.model.Work.query.filter_by(source=source).first()
        assert out.creators[0].full_name == u'Phil Medley'
        assert out.creators[1].full_name == u'Bert Russell Berns', out.creators[1].full_name
        perf = out.performances[0]
        assert perf.performers[0].full_name == u'The Beatles'

    def test_beethoven_violin(self):
        source = self.loader._mb_source(self.beethoven_violin.id)
        out = mb2dm.model.Work.query.filter_by(source=source).first()
        print out.creators
        assert out.creators[0].full_name == u'Ludwig van Beethoven'
        perf = out.performances[0]
        assert perf.performers[0].full_name == u'Arturo Toscanini'
        assert perf.performers[1].full_name == u'NBC Symphony Orchestra'

    def test_pixinguinha(self):
        source = self.loader._mb_source(self.pixinguinha.id)
        out = mb2dm.model.Work.query.filter_by(source=source).first()
        assert out.creators[0].full_name == u'Pixinguinha'
        perf = out.performances[0]
        assert perf.performers[0].full_name == u'Pixinguinha'
        assert out.creators[0].id == perf.performers[0].id

    def test_no_duplicates(self):
        self.pixinguinha2 = pdw.getdata.mb.get_track(
                u'http://musicbrainz.org/track/73a473d1-eed8-4c86-8ca0-a5c9201b5ad3')
        self.loader.load_track(self.pixinguinha2, None)
        mb2dm.model.Session.commit()
        mb2dm.model.Session.clear()
        out = mb2dm.model.Artist.query.filter_by(full_name=u'Pixinguinha').all()
        assert len(out) == 1


