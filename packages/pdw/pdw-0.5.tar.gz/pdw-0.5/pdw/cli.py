import os
import logging
logger = logging.getLogger('pdw.cli')

import paste.script

# TODO: use verbose level to set logger level
class Command(paste.script.command.Command):
    parser = paste.script.command.Command.standard_parser(verbose=True)
    parser.add_option('-c', '--config', dest='config',
            default='development.ini', help='Config file to use.')
    parser.add_option('-f', '--file',
        action='store',
        dest='file_path',
        help="File to dump results to (if needed)")
    default_verbosity = 1

    def _load_config(self):
        from paste.deploy import appconfig
        from pdw.config.environment import load_environment
        if not self.options.config:
            msg = 'No config file supplied'
            raise self.BadCommand(msg)
        self.filename = os.path.abspath(self.options.config)
        conf = appconfig('config:' + self.filename)
        load_environment(conf.global_conf, conf.local_conf)
        import pdw.model as model
        model.binddb()

    def _setup_app(self):
        cmd = paste.script.appinstall.SetupCommand('setup-app') 
        cmd.run([self.filename]) 


class Db(Command):
    '''Perform various tasks on the database.
    
    db create
    db clean
    db consolidate
    db pgdump # db pgdump > {file}
    db pgload # db pgload < {file}
    db dump {file_path} # dump to json format
    db load {file_path} # load from json format
    db stat
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def command(self):
        self._load_config()
        cmd = self.args[0]
        from pdw import model
        if cmd == 'create':
            model.repo.create_db()
        elif cmd == 'init':
            model.repo.create_db()
        elif cmd == 'clean':
            model.repo.clean_db()
        elif cmd == 'load' or cmd == 'dump':
            self.dump_or_load(cmd)
        elif cmd == 'pgdump' or cmd == 'pgload':
            self.pg_dump_or_load(cmd)
        elif cmd == 'stat':
            model.repo.stat_db()
        else:
            print 'Command %s not recognized' % cmd

    def dump_or_load(self, cmd):
        if len(self.args) < 2:
            print 'Need dump path'
            return
        dump_path = self.args[1]
        import pdw.serialize
        import pdw.model as model
        # default seems to be 1
        verbose = self.verbose > 1
        dumper = pdw.serialize.Dumper([
            model.Person,
            model.Work,
            model.Item,
            model.WorkItem,
            model.WorkPerson,
            model.ItemPerson,
            model.Sale,
            model.Extra,
            ],
            verbose=verbose
            )
        if cmd == 'load':
            logger.info('Db load %s' % repr(dump_path) )
            if os.path.isdir(dump_path):
                dumper.load(dump_path)
            else:
                dumper.load(open(dump_path))
        elif cmd == 'dump':
            # TODO: check to avoid overwriting existing material ...
            if dump_path.endswith('.js'):
                dumper.dump(open(dump_path, 'w'))
            else: # assume a directory
                dumper.dump(dump_path)
        else:
            print 'Unknown command', cmd

    def pg_dump_or_load(self, cmd):
        from pylons import config
        # dburi = config['sqlalchemy.url']
        dburi = config['pylons.g'].sa_engine.url
        assert dburi.drivername == 'postgres', 'Only works with postgres'
        os.environ['PGPASSWORD'] = dburi.password
        if cmd == 'pgdump':
            basecmd = 'pg_dump'
        else:
            import pdw.model as model            
            logger.info('Db pgload' )
            basecmd = 'psql'
        cmdline = '%s -h %s --user %s %s' % (basecmd, dburi.host,
                dburi.username, dburi.database)
        if cmd == 'pgdump':
            cmdline += ' --data-only'
        os.system(cmdline)


class Load(Command):
    '''Load data from various sources.
    
    load ngcoba | ngcoba2 | charm | betts
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def command(self):
        self._load_config()
        self._setup_app()
        cmd = self.args[0]
        logger.info('Load %s' % repr(self.args))
        if cmd == 'demo':
            self.load_demo()
        elif cmd == 'ngcoba':
            self.load_ngcoba()
        elif cmd == 'ngcoba2':
            self.load_ngcoba2()
        elif cmd == 'charm':
            if len(self.args) > 1:
                index = None
                subset = self.args[1]
                if len(self.args) > 2:
                    index = int(self.args[2])
                self.load_charm(subset, index)
            else:
                self.load_charm()
        elif cmd == 'betts':
            if len(self.args) > 1:
                subset = self.args[1]
                self.load_betts(subset)
            else:
                print "Need to specify which betts file to load. Try: 'marc_loc_updates' or 'all'"
        else:
            print 'Command not recognized'
    
    def load_demo(self):
        import pkg_resources
        import pdw.getdata.openlibrary as openlibrary
        import pdw.model as model
        loader = openlibrary.Loader()
        fo = pkg_resources.resource_stream('pdw', 'tests/data/openlibrary.authors.json')
        fo2 = pkg_resources.resource_stream('pdw', 'tests/data/openlibrary.editions.json')
        [ xx for xx in loader.load_authors(fo) ]
        [ xx for xx in loader.load_editions(fo2) ]
        model.Session.commit()
    
    def load_ngcoba(self):
        import time
        import pdw.getdata.ngcoba as ngcoba
        cache_path = os.path.join('cache', 'ngcoba')
        loader = ngcoba.Loader()
        fns = os.listdir(cache_path)
        fns.sort()
        # ignore all items starting with 0 or with 0 as their second letter
        # as contain weird/unusual names (e.g. numbers, single letters etc)
        fns = filter(lambda x: not(x[0] in ['0', '1'] or x[1] == '0'), fns)
        start = time.time()
        # skip_until = 'Ha3.htm'
        skip_until = ''
        skip = True
        for fn in fns:
            if not skip_until or fn == skip_until: skip = False
            if skip: continue
            fp = os.path.join(cache_path, fn)
            print '=============== Processing: %s =============' % fp
            loader.load_to_db(open(fp))
            print '======== Time so far: %s' % (time.time() - start)
        end = time.time()
        print 'Time elapsed:', end-start

    def load_ngcoba2(self):
        import time
        import pdw.getdata.ngcoba2 as ngcoba
        loader = ngcoba.Loader()
        start = time.time()
        cache_path = os.path.join('cache', 'ngcoba2')
        fp = os.path.join(cache_path, 'ngcoba2.txt')
        print '=============== Processing: %s =============' % fp
        fileobj = open(fp)
        try:
            loader.load_to_db(fileobj)
        finally:
            fileobj.close()
        end = time.time()
        print 'Time elapsed:', end-start

    def load_charm(self, subset=None, index=None):
        import time
        import pdw.getdata.charm as charm 
        charmdata = charm.CharmData()
        print 'Downloading'
        charmdata.download()
        charmdata.load_data(data_name=subset, index=index)

    def load_betts(self, subset):
        import time
        import pdw.getdata.marc as marc
        loader = marc.ParserOpenLibrary()
        start = time.time()
        loader.load_to_db_by_name(subset)
        end = time.time()
        print 'Time elapsed:', end-start
        

class Stats(Command):
    '''Statistics on data in db.
    
    stats basic | person_dups | item_dups
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def command(self):
        self._load_config()
        cmd = self.args[0]
        if cmd == 'basic':
            self.basic()
        elif cmd == 'person_dups':
            self.person_dups()
        elif cmd == 'item_dups':
            self.item_dups()
        else:
            print 'Command not recognized'

    def basic(self):
        import pdw.stats
        results = pdw.stats.basic_info()
        print results
        # out = u''
        # for cls in pdw.stats.main_classes:
        #    out += '''### '''

    def person_dups(self):  
        import pdw.model as model
        import sqlalchemy.sql as sql
        # q = sql.select(model.person_table)
        q = model.Person.query
        sqlq = '''SELECT name, birth_date, count(*), srcid FROM person 
        WHERE name != '' AND name is not null AND birth_date is not NULL AND
        birth_date != 'None'
        GROUP BY name, birth_date
        HAVING count(*) > 1
        ORDER BY count(*) DESC;
        '''
        myq = sql.text(sqlq)
        print myq
        engine = model.metadata.bind
        for idx, item in enumerate(engine.execute(myq)):
            print item
            if idx > 10:
                break
        # q.group_by(model.Person.name, model.Person.birth_date)
        # q.having

    def item_dups(self):
        import pdw.model as model
        import sqlalchemy.sql as sql
        sqlq = '''SELECT item.title, person.name, count(*) FROM
        item JOIN item_2_person on item.id = item_2_person.item_id
        JOIN person on person.id = item_2_person.person_id
        GROUP BY item.title, person.name
        HAVING count(*) > 1
        ORDER BY count(*) DESC
        LIMIT 10;
        '''
        myq = sql.text(sqlq)
        print myq
        engine = model.metadata.bind
        for idx, item in enumerate(engine.execute(myq)):
            print item
            if idx > 10:
                break
        # q.group_by(model.Person.name, model.Person.birth_date)
        # q.having


class Consolidate(Command):
    '''Consolidate data in db.
    
    consolidate person | item2work
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def command(self):
        self._load_config()
        cmd = self.args[0]
        import pdw.consolidate
        if cmd == 'person':
            pdw.consolidate.consolidate_persons(verbose=True)
        elif cmd == 'item2work':
            pdw.consolidate.items_to_works(verbose=True)
        else:
            print 'Command not recognized'
