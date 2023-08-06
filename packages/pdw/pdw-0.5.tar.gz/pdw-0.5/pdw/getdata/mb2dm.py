'''Load MusicBrainz data into our domain model.


Issues with musicbrainz:

    1. No distinction between work and performance.
        1. This means we have to operate per track which means that classical
        pieces get incorrectly split up.
    2. Ambiguity between creators/composers and performers on most tracks.
'''
import time

import pdw.model as model
import pdw.mb
import pdw.copyright
from pdw.parse_composer_data import parse_date

def setup_config(config_file):
    from paste.deploy import loadapp, CONFIG
    import paste.deploy
    conf = paste.deploy.appconfig('config:' + config_file)
    CONFIG.push_process_config({'app_conf': conf.local_conf,
                                'global_conf': conf.global_conf}) 

def calculate_copyright_status_for_db():
    for performance in model.Performance.select():
        status = calculate_copyright_status(performance)
        performance.copyright_status = status
        pdw.models.commit()

class MusicBrainzLoader:
    '''

    MusicBrainz metadata summary:
    =============================

    * On most releases primary artist is the performer
    * On classical releases Primary Artist is the composer [1][2]
    * A release = An Album and on most early work no consistency across Album
      so we will focus on Tracks as equivalent of works (though this is not
      really correct ...)

    Questions
    ---------
    
    1. Can we access advanced relationships [3] from the python API?
    2. What part of release info gives link to mb site url?
    3. Release events seem to be missing on material returned by python
    bindings[^1]
    
    (see e.g. [4])

    [1]: http://musicbrainz.org/doc/PrimaryArtistForClassicalReleases
    [2]: http://wiki.musicbrainz.org/ClassicalMusicFAQ
    [3]: http://musicbrainz.org/doc/AdvancedRelationships
    [4]: http://musicbrainz.org/ws/1/release/2ebe9842-38bc-4b6c-a541-6abf807f0dd3?type=xml&inc=artist+counts+release-events+discs+tracks

    Ask questions on: http://musicbrainz.org/doc/DevelopersMailingList

    [^1]: for example we have

    >>> out[0].__dict__
        {'_types': [u'http://musicbrainz.org/ns/mmd-1.0#Album',
        u'http://musicbrainz.org/ns/mmd-1.0#Official'], '_discs': [],
        '_textScript': u'Latn', '_tracks': [], '_releaseEvents': [], '_relations':
        {}, '_textLanguage': u'ENG', '_tracksCount': 3, '_tracksOffset': None,
        '_artist': <musicbrainz2.model.Artist object at 0x12b1b90>, '_id':
        u'http://musicbrainz.org/release/2ebe9842-38bc-4b6c-a541-6abf807f0dd3',
        '_title': u'Sonorous Songs Of Sarangi', '_asin': None}
    >>> out[0].releaseEvents
        []

    Yet [4] displays the correct data.
    '''

    def __init__(self, start_date='19000101', end_date='19100101', sleep=1):
        self.start_date = start_date
        self.end_date = end_date
        self.verbose = True
        self.sleep = sleep

    def _p(self, msg, force=False):
        if force or self.verbose:
            print(msg.encode('utf8'))

    def execute(self):
        # TODO break it up so we do not get hit by record limit
        limit = 100
        out = pdw.mb.find_releases_by_date(self.start_date, self.end_date,
                limit=100)
        # do not hit MB server with more than 1 request a second
        # do this most places we make a request
        time.sleep(self.sleep)
        total = len(out)
        print '## %s Releases to process' % total
        for release in out:
            msg = 'Processing %s' % release.title
            self._p(msg)
            self.load_release(release)
        model.Session.commit()

    def load_release(self, release):
        # first get more info as find_releases_by_date gets quite an anaemic
        # version of each release with little info
        rel = pdw.mb.get_release(release.id)
        time.sleep(self.sleep)
        release_date = rel.getEarliestReleaseDate()
        for track in rel.tracks:
            # get the extra info including relations
            full_track = pdw.mb.get_track(track.id)
            msg = '-- Processing track: %s' % track.title
            self._p(msg)
            self.load_track(full_track, release_date)
            time.sleep(self.sleep)
            # commit after each track because o/w select will miss stuff
            model.Session.commit()

    def load_track(self, track, release_date):
        '''
        # mb does not distinguish work and performance ...
        # we always create a work and performance for each release
        # TODO: how do distinguish between creators and performers?
        # one idea: compare release artist and track artist
        # also look at relations
        # see http://lists.musicbrainz.org/pipermail/musicbrainz-users/2004-February/004855.html
        # for classical normally main artist
        # for other stuff may need advanced relationships ...
        # TODO
        # if '...Classical' in release.type:
        #    pass
        '''
        if self._existing_item(model.Work, track.id):
            msg = '-> Skipping %s (%s) as already exists in db' % (track.title,
                    track.id)
            self._p(msg)
            return
        wrk = model.Work(title=track.title)
        wrk.source = self._mb_source(track.id)
        track_artists = self.get_track_artists(track)
        composers, performers = self.get_track_relations(track)
        if composers:
            for comp in composers:
                wrk.creators.append(comp)
        else:
            for cc in track_artists:
                wrk.creators.append(cc)
        # do not check it already exists since this was done for Work
        prfm = model.Performance(work=wrk,
                performance_date=release_date,
                source=self._mb_source(track.id),
                )
        if performers:
            for performer in performers:
                prfm.performers.append(performer)
        else:
            for cc in track_artists:
                prfm.performers.append(cc)
        if release_date:
            prfm.performance_date = parse_date(release_date)

    def get_track_relations(self, track):
        out = []
        # TODO: expand this ...
        performer_types = [
                u'http://musicbrainz.org/ns/rel-1.0#Conductor',
                u'http://musicbrainz.org/ns/rel-1.0#PerformingOrchestra',
                ]
        composer_types = [
            u'http://musicbrainz.org/ns/rel-1.0#Composer',
            ]
        composers = []
        performers = []
        for rel in track.getRelations():
            if rel.type in composer_types:
                artist = self.get_artist(rel.target)
                composers.append(artist)
            if rel.type in performer_types:
                artist = self.get_artist(rel.target)
                performers.append(artist)
        return composers, performers

    def get_track_artists(self, track):
        '''Always return the track artist ...

        Currently only ever one but have more at some point so return a list.
        '''
        out = self.get_artist(track.artist)
        if out:
            return [out]
        else:
            return []

    def get_artist(self, mb_artist):
        if mb_artist is None:
            return None
        out = self._existing_item(model.Artist, mb_artist.id)
        if out:
            return out
        else: # create new object
            src = self._mb_source(mb_artist.id)
            artist = model.Artist(
                    source=src,
                    full_name=mb_artist.name,
                    birth_date=parse_date(mb_artist.beginDate),
                    death_date=parse_date(mb_artist.endDate),
                    )
            # commit because o/w select will not pick up new item
            model.Session.commit()
            return artist

    def _mb_source(self, mb_id):
        return model.source_encode('mb', mb_id)

    def _existing_item(self, obj_class, mb_id):
        src = self._mb_source(mb_id)
        out = obj_class.query.filter_by(source=src).first()
        return out

