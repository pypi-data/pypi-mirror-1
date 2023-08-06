import datetime, time
import calendar
import feedparser
import pkg_resources

from genshi.builder import tag
from trac.core import *
from trac.config import ListOption
from trac.admin.api import IAdminPanelProvider
from trac.timeline.api import ITimelineEventProvider
from trac.util import format_datetime
from trac.util.translation import _
from trac.web.chrome import ITemplateProvider, INavigationContributor
from trac.web import IRequestHandler

from insidetrac.model import FeedConfig, FeedEntries

pluginprefix='insidetrac'

class RSSFeedReader(Component):
    implements(ITimelineEventProvider, IAdminPanelProvider, ITemplateProvider, IRequestHandler, INavigationContributor)
    
    # ITimelineEventProvider methods    
    def get_timeline_filters(self, req):
        for feed in FeedConfig.all_feeds(self.env):
            yield ('%s-%s' % (pluginprefix, feed.shortname), 'RSS: %s' % (feed.longname))
    
    def get_timeline_events(self, req, start, stop, filters):
        if isinstance(start, datetime.datetime): # Trac>=0.11
            from trac.util.datefmt import to_timestamp
            start = to_timestamp(start)
            stop = to_timestamp(stop)

        for feed in FeedConfig.all_feeds(self.env):
            feedkey = '%s-%s' % (pluginprefix, feed.shortname)
            if feedkey in filters:
                for entry in FeedEntries.return_entries(self.env.get_db_cnx(), feed.id, start, stop):
                    yield (feedkey, entry[3], "InsideTrac: %s - %s" % (feed.shortname, entry[2]), entry[1], entry[4], entry[5])
                    
    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('insidetrac', _('InsideTrac'), 'feeds', _('RSS Feeds'))
        
    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('TRAC_ADMIN')
        if req.method == 'POST':
            self.env.log.debug("Got here!")
            for feedname in req.args:
                if feedname.startswith('feed_full_name_'):
                    feedid = feedname.split('_')[-1]
                    if feedid == 'new':
                        longname = ' '.join(req.args['feed_full_name_new'].split())
                        shortname = ' '.join(req.args['feed_short_name_new'].split())
                        url = ' '.join(req.args['feed_url_new'].split())
                        if longname and shortname and url:
                            feed = FeedConfig(self.env)
                            feed.longname = longname
                            feed.shortname = shortname
                            feed.url = url
                            feed.insert()
                    else:
                        try:
                            feedid = int(feedid)
                            feed = FeedConfig(self.env, feedid)
                            if 'feed_delete_%d' % (feedid) in req.args:
                                feed.delete()
                            else:
                                longname = ' '.join(req.args['feed_full_name_%d' % (feedid)].split())
                                shortname = ' '.join(req.args['feed_short_name_%d' % (feedid)].split())
                                url = ' '.join(req.args['feed_url_%d' % (feedid)].split())
                                feed.longname = longname or feed.longname
                                feed.shortname = shortname or feed.shortname
                                feed.url = url or feed.url
                                feed.update()
                        except ValueError:
                            pass
        return 'insidetrac_admin.html', {"feeds": FeedConfig.all_feeds(self.env)}
    
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('insidetrac', 'templates')]

    
    # IRequestHandlerMethods
    def match_request(self, req):
        return req.path_info.startswith('/insidetracupdatefeeds') or req.path_info.startswith('/insidetrac.user.js')
    
    def process_request(self, req):
        if req.path_info.startswith('/insidetracupdatefeeds'):
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
            req.send('success!')
        elif req.path_info.startswith('/insidetrac.user.js'):
            return ('insidetrac.user.js', {'abs_href': req.abs_href, 'addname': self.env.project_name}, 'text/plain')
    
    def scrub_entries(self, older):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute('delete from feedentries where completed < %s', (older,))
        db.commit()

    # INavigationContributor Methods
    def get_active_navigation_item(self, req):
        return 'greasemonkey'
    
    def get_navigation_items(self, req):
        yield ('metanav', 'greasemonkey', tag.a(_('InsideTrac GM'), href='%s/insidetrac.user.js' % (req.abs_href.base), title=_('InsideTrac GreaseMonkey Script')))
    