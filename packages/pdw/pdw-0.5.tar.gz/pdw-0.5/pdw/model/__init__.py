import time

from meta import *
from pdw.name import *
# from work import *
from frbr import *
from sale import sale_table, Sale

REPO_LOG_FNAME = '/tmp/pdw.repo.log'

class Repository(object):
    def __init__(self, ourmetadata, oursession):
        self.metadata = ourmetadata
        self.session = oursession

    def create_db(self):
        self.log('Create')
        self.metadata.create_all(bind=self.metadata.bind)

    def clean_db(self):
        self.log('Clean')
        self.metadata.drop_all(bind=self.metadata.bind)

    def rebuild_db(self):
        self.clean_db()
        self.create_db()

    def stat_db(self):
        def percent(numerator, denominator):
            if denominator == 0:
                return 0
            return int(float(numerator) / denominator * 100)

        msg = []
        m = 'DB stat for %s\n' % config['pylons.g'].sa_engine
        print m; msg.append('DB stat')

        num_persons = self.session.query(Person).count()
        num_persons_with_bdate = self.session.query(Person).filter(Person.birth_date!=None).count()
        m = "%i persons (%i%% have bdate)" % (num_persons, percent(num_persons_with_bdate, num_persons))
        print m; msg.append(m)
        
        num_items = self.session.query(Item).count()
        num_items_with_date = self.session.query(Item).filter(Item.date!=None).count()
        m = "%i items (%i%% have date)" % (num_items, percent(num_items_with_date, num_items))
        print m; msg.append(m)

        num_works = self.session.query(Work).count()
        num_works_with_date = self.session.query(Work).filter(Work.date!=None).count()
        m = "%i works (%i%% have date)" % (num_works, percent(num_works_with_date, num_works))
        print m; msg.append(m)
        self.log('\n'.join(msg))

    def log(self, msg):
        db_name = config['pylons.g'].sa_engine
        date_time = time.asctime()
        f = open(REPO_LOG_FNAME, 'a')
        try:
            f.write("%s %s: %s\n" % (db_name, date_time, msg))
        finally:
            f.close()

repo = Repository(metadata, Session)

