try:
    import pdw.getdata.mb
except:
    __test__ = False

# johann sebastian bach
jsb_id = 'http://musicbrainz.org/artist/24f1766e-9635-4d58-a4d4-9413f9f98a4c'  

class TestFindArtist:
    __test__ = False

    def test_unknown(self):
        artist_name = 'NoArtistHasThisName'
        out = pdw.getdata.mb.find_artist(artist_name)
        assert out is None

    def test_1(self):
        artist_name = 'Johann Sebastian Bach'
        out = pdw.getdata.mb.find_artist(artist_name)
        assert out == jsb_id

class TestGetArtist:
    __test__ = False

    def test_jsb(self):
        out = pdw.getdata.mb.get_artist(jsb_id)
        assert out.id == jsb_id

class TestGetRelease:
    __test__ = False

    def test_1(self):
        id = u'http://musicbrainz.org/release/b220a779-570f-4ec8-a38a-f525a4b061bb'
        out = pdw.getdata.mb.get_release(id)
        exp_title = u'Oh How That German Could Love! / My Little Dutch Colleen'
        assert out.title == exp_title, out.title
        assert len(out.tracks) == 2
        assert out.getEarliestReleaseDate() == u'1910'

class TestFindReleasesByDate:
    __test__ = False

    def test_find_releases_by_date(self):
        start_date = '19000101'
        end_date = '19100101'
        releases = pdw.getdata.mb.find_releases_by_date(start_date, end_date)
        # getEarliestReleaseDate
        # getReleaseEvents only introduced in mb2 0.4.0 release
        # 2008-09-12 this stuff does seem to change over time ...
        # exp_title = 'Columbia A-0804'
        exp_title = u'Goodbye My Honey'
        print [ r.title for r in releases ]
        out_title = releases[0].title
        assert out_title == exp_title, (out_title, exp_title)
        # because using a filter do not get this kind of extra info
        # need to search per release using id and use a ReleaseIncludes item
        # outdate = releases[0].getEarliestReleaseDate()
        # assert outdate == '1910'
        assert len(releases) == 25, len(releases)

    def test_release_statistics(self):
        start = 1906
        end = 1911
        out = pdw.getdata.mb.release_statistics(start, end)
        assert len(out) == 5
        assert out[-1][0] == 1910
        assert out[-1][1] == 3, out[-1][1]


