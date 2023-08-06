import calendar
import datetime
import time
import feedparser

from trac.util.translation import _
from trac.core import *
from trac.db import Table, Column, Index, DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.resource import ResourceNotFound
from tracscheduler.web_ui import IScheduledTask

class DBFeedConfig(Component):
    implements(IEnvironmentSetupParticipant)
    
    feedcfg = Table('feed', key='id')[
        Column('id', auto_increment=True),
        Column('longname'),
        Column('shortname'),
        Column('url')
        ]
    
    def environment_created(self):
        self.make_base_table(None)
    
    def environment_needs_upgrade(self, db):
        try:
            db.cursor().execute('select * from feed')
        except:
            return True
        return False
    
    def upgrade_environment(self, db):
        self.make_base_table(db)
    
    def make_base_table(self, db=None):
        if not db:
            db = self.env.get_db_cnx()
        cursor = db.cursor()
        db_connector, discard = DatabaseManager(self.env)._get_connector()
        for stmt in db_connector.to_sql(self.feedcfg):
            cursor.execute(stmt)
    
class FeedConfig(object):
    def __init__(self, env, feedid=None, db=None):
        try:
            feedid = int(feedid)
        except:
            feedid = None
        self.env = env
        self.id = feedid
        self.longname = None
        self.shortname = None
        self.url = None
        
        if self.id and db:
            self._fetch(self.id, db)
        
    def _fetch(self, feedid, db=None):
        if not db:
            db = self.env.get_db_cnx()
        if feedid:
            cursor = db.cursor()
            cursor.execute('select id, longname, shortname, url from feed where id=%s', (feedid, ))
            row = cursor.fetchone()
            if not row:
                raise ResourceNotFound('Feed id %d does not exist!' % (feedid))
            self._from_database(row)
    
    def _from_database(self, row):
        feedid, longname, shortname, url = row
        self.id = feedid
        self.longname = longname or ''
        self.shortname = shortname or ''
        self.url = url or ''
      
    @classmethod
    def all_feeds(cls, env):
        db = env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute('select id from feed')
        row = cursor.fetchone()
        while row:
            yield FeedConfig(env, row[0], db)
            row = cursor.fetchone()
            
    def delete(self, db=None):
        if not db:
            db = self.env.get_db_cnx()
            handle_ta = True
        else:
            handle_ta = False
            
        cursor = db.cursor()
        self.env.log.debug('Deleting feed id %d' % (self.id))
        cursor.execute('delete from feed where id=%s', (self.id, ))
        
        if handle_ta:
            db.commit()
    
    def insert(self, db=None):
        assert self.longname, 'Cannot insert feed without long name'
        assert self.shortname, 'Cannot insert feed without short name'
        assert self.url, 'Cannot insert feed without url'
        
        if not db:
            db = self.env.get_db_cnx()
            handle_ta = True
        else:
            handle_ta = False
            
        cursor = db.cursor()
        longname = ' '.join(self.longname.split())
        shortname = ' '.join(self.shortname.split())
        url = ' '.join(self.url.split())
        self.env.log.debug('Inserting new feed: longname=%s, shortname=%s, url=%s' % (longname, shortname, url))
        cursor.execute('insert into feed(longname, shortname, url) values(%s,%s,%s)', (longname, shortname, url))
        
        if handle_ta:
            db.commit()
    
    def update(self, db=None):
        assert self.id, 'Cannot update feed that has not been stored to database'
        assert self.longname, 'Cannot set feed to have no long name'
        assert self.shortname, 'Cannot set feed to have no short name'
        assert self.url, 'Cannot set feed to have no url'
        
        if not db:
            db = self.env.get_db_cnx()
            handle_ta = True
        else:
            handle_ta = False
            
        cursor = db.cursor()
        longname = ' '.join(self.longname.split())
        shortname = ' '.join(self.shortname.split())
        url = ' '.join(self.url.split())
        self.env.log.debug('Updating feed id %d: longname=%s, shortname=%s, url=%s' % (self.id, longname, shortname, url))
        cursor.execute('update feed set longname=%s, shortname=%s, url=%s where id=%s', (longname, shortname, url, self.id))
        
        if handle_ta:
            db.commit()

class DBFeedEntries(Component):
    implements(IEnvironmentSetupParticipant)
    
    feedentries = Table('feedentries', key='id')[
        Column('feedid', type='int'),
        Column('completed', type='int'),
        Column('title'),
        Column('link'),
        Column('author'),
        Column('summary')
        ]

    def environment_created(self):
        self.make_base_table(None)
    
    def environment_needs_upgrade(self, db):
        try:
            db.cursor().execute('select * from feedentries')
        except:
            return True
        return False
    
    def upgrade_environment(self, db):
        self.make_base_table(db)
    
    def make_base_table(self, db=None):
        if not db:
            db = self.env.get_db_cnx()
        cursor = db.cursor()
        db_connector, discard = DatabaseManager(self.env)._get_connector()
        for stmt in db_connector.to_sql(self.feedentries):
            cursor.execute(stmt)

class FeedEntries(Component):
    implements(IScheduledTask)
            
    def process_scheduled_task(self, parent):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        for feed in FeedConfig.all_feeds(self.env):
            d = feedparser.parse(feed.url)
            for entry in d.entries:
                completed = calendar.timegm(entry.date_parsed)
                for attr in ('title', 'link', 'author', 'summary'):
                    if not hasattr(entry, attr): setattr(entry, attr, '')
                parms = (feed.id, completed, entry.title, entry.link, entry.author, entry.summary)
                cursor.execute('select feedid, completed, title, link, author, summary from feedentries where feedid=%s and completed=%s and title=%s and link=%s and author=%s and summary=%s', parms)
                row = cursor.fetchone()
                if not row:
                    cursor.execute('insert into feedentries(feedid, completed, title, link, author, summary) values (%s,%s,%s,%s,%s,%s)', parms)
        self.scrub_entries(time.mktime(datetime.datetime.now().timetuple())-(86400*90))
        db.commit()
    
    def scrub_entries(self, older):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute('delete from feedentries where completed < %s', (older,))
        db.commit()
    
    @classmethod
    def return_entries(cls, db, feedid, start, stop):
        cursor = db.cursor()
        cursor.execute('select distinct feedid, completed, title, link, author, summary from feedentries where feedid=%s and completed >= %s and completed <= %s', (feedid, start, stop))
        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()

