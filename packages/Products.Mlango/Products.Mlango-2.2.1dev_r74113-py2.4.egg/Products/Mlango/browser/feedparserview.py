#!/usr/bin/python
# Copyright (C) 2008  Goldmund, Wyldebeast & Wunderliebe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

class Feedparser:
    
      
    def parse(self, url, entry_fields=['title', 'link'], feed_fields=['title']):
    
        """
        Parse given feed, and create a simple dictionary with a feed and a entries
        field. 
        """
        try:
            import feedparser
        except:
            self.context.plone_log('Unable to import feedparser')
            from Products.Mlango import feedparser
        
        data = feedparser.parse(url) # feedparser.FeedParserDict
      
        entries = []
        feed = {}
      
        for f in feed_fields:
            feed[f] = data.feed.get(f, '')
    
        # very simple one for now
        for e in data.entries:
            entry = {}
            for f in entry_fields:
                self.context.plone_log('ENTRY f: %s  e.get: %s ' % (f, e.get(f, '').encode('utf8')))
                entry[f] = e.get(f, '').encode('utf8')         
            entries.append(entry)
    
    
        return {'feed':feed, 'entries':entries}
