# package for musicbrainz related code
import urllib
import logging
import musicbrainz2.webservice as ws
import musicbrainz2.model as m
import musicbrainz2.wsxml as wsxml


# config debugging because used by musicbrainz2 internally
# TODO:? move this to somewhere more core?
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEBUG = True


def find_artist(artist_name):
    """Search for all artists matching the given name.

    Limit the results to the 5 best matches.
    The offset parameter could be used to page through the results.
    """
    q = ws.Query()
    f = ws.ArtistFilter(name=artist_name, limit=5)
    artistResults = q.getArtists(f)
    if DEBUG:
        for result in artistResults:
            artist = result.artist
            print "Score     :", result.score
            print "Id        :", artist.id
            print "Name      :", artist.name
            print "Sort Name :", artist.sortName
            print
    if len(artistResults) == 0:
        return None
    else:
        result = artistResults[0]
        artist = result.artist 
        # must do better than this to count as a match
        cutoff_score = 80
        # could also try checking name is an exact match ...
        # require(artist.name == artist_name or artist.sortName == artist_name)
        if result.score < cutoff_score:
            # todo log something
            return None
        return artist.id

def get_artist(id):
    q = ws.Query()
    inc = ws.ArtistIncludes(
        releases=(m.Release.TYPE_OFFICIAL, m.Release.TYPE_ALBUM))
    artist = q.getArtistById(id, inc)
    return artist

def show_artist(id):
    artist = get_artist(id)
    print "Id         :", artist.id
    print "Name       :", artist.name
    print "SortName   :", artist.sortName
    print "UniqueName :", artist.getUniqueName()
    print "Type       :", artist.type
    print "BeginDate  :", artist.beginDate
    print "EndDate    :", artist.endDate
    print

    if len(artist.getReleases()) == 0:
        print "No releases found."
    else:
        print "Releases:"

    for release in artist.getReleases():
        print
        print "Id        :", release.id
        print "Title     :", release.title
        print "ASIN      :", release.asin
        print "Text      :", release.textLanguage, '/', release.textScript
        print "Types     :", release.types


def get_release(id):
    q = ws.Query()
    # do minimum for what we need
    inc = ws.ReleaseIncludes(artist=True, releaseEvents=True,
            tracks=True)
            # discs=True, tracks=True,
            # artistRelations=True, releaseRelations=True,
            # trackRelations=True, urlRelations=True)
    release = q.getReleaseById(id, inc)
    return release


def get_track(id):
    q = ws.Query()
    # do minimum for what we need
    # inc = ws.TrackIncludes(artist=True, releases=True, trackRelations=True,
    #        urlRelations=True, artistRelations=True)
    inc = ws.TrackIncludes(artist=True, artistRelations=True)
    track = q.getTrackById(id, inc)
    return track


def find_releases_by_date(start_date='18000101', end_date='19000101', limit=25,
        offset=0):
    """Get all releases between `start_date' and `end_date'.
    
    Dates should be in form 20010101.

    limit and offset parameters as described in:

        http://wiki.musicbrainz.org/XMLWebService

    limit: An integer value defining how many entries should be returned. Only
    values between 1 and 100 (both inclusive) are allowed. If not given, this
    defaults to 25.

    offset: Return search results starting at a given offset. Used for paging
    through more than one page of results. 
    """
    # no support in api for date stuff so do it by hand
#    url = 'http://musicbrainz.org/ws/1/release/?type=xml&query=date:[' + \
#        start_date + '%20TO%20' +  end_date + ']'
#    logger.debug('url for date search: %s' % url)
#    parser = wsxml.MbXmlParser()
#    myxml = urllib.urlopen(url)
#    meta = parser.parse(myxml)
#    results = meta.getReleaseResults()
    date_query = 'date:[%s TO %s]' % (start_date, end_date)
    q = ws.Query()
    f = ws.ReleaseFilter(query=date_query, limit=limit, offset=offset)
    results = q.getReleases(f)
    releases = [ r.release for r in results ]
    return releases

def release_statistics(start_year, end_year):
    """Get release holdings by year.
    """
    results = []
    for year in range(start_year, end_year):
        tyear = str(year)
        releases = find_releases_by_date(tyear, tyear)
        tnum = len(releases)
        results.append((year, tnum))
    return results

