#!/usr/bin/env python

try:
    import xml.etree.ElementTree as ET # in python >=2.5
except ImportError:
    try:
        import cElementTree as ET # effbot's C module
    except ImportError:
        try:
            import elementtree.ElementTree as ET # effbot's pure Python module
        except ImportError:
            try:
                import lxml.etree as ET # ElementTree API using libxml2
            except ImportError:
                import warnings
                warnings.warn("could not import ElementTree " "(http://effbot.org/zone/element-index.htm)")
                # Or you might just want to raise an ImportError here.
                raise

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import iso8601
import genshi

class HCalendar(object):
    def __init__(self, content):
        self.content = content

    def get_events(self):
        vevents = []
        for event, elem in ET.iterparse(self.content):
            classes = elem.get('class')
            if classes:
                if 'vevent' in classes:
                    vevents.append(elem)

        for vevent in vevents:
            vevent_data = {}
            for elem in self.flatten_element(vevent):
                classes = elem.get('class', None)
                if classes:
                    for class_ in classes.split(" "):
                        func = getattr(self, "handle_%s" % (class_,),
                            None)
                        if func:
                            func(vevent_data, elem)

            if self.has_enough_data(vevent_data):
                vevent_data['description'] = ET.tostring(vevent)
                yield vevent_data

    def flatten_element(self, elem, yieldself = True):
        if yieldself:
            yield elem
        for e in elem:
            yield e
            for e1 in self.flatten_element(e, yieldself = False):
                yield e1

    def text_for_elem(self, elem):
        if elem.tag != "abbr":
            return elem.text
        else:
            return elem.get('title', elem.text)

    def parse_date(self, date_str):
        try:
            return iso8601.parse_date(date_str)
        except:
            return None

    def handle_dtstart(self, vevent_data, elem):
        date_str = self.text_for_elem(elem)
        date_obj = self.parse_date(date_str)
        if date_obj:
            vevent_data['dtstart'] = date_obj

    def handle_dtend(self, vevent_data, elem):
        date_str = self.text_for_elem(elem)
        date_obj = self.parse_date(date_str)
        if date_obj:
            vevent_data['dtend'] = date_obj

    def handle_url(self, vevent_data, elem):
        vevent_data['url'] = elem.get('href')

    def handle_summary(self, vevent_data, elem):
        vevent_data['summary'] = self.text_for_elem(elem)

    def handle_location(self, vevent_data, elem):
        vevent_data['location'] = self.text_for_elem(elem)

    def has_enough_data(self, vevent_data):
        fields_to_check = [
            'summary',
            'dtstart',
            'dtend',
            'url',
            'location',
        ]
        for field in fields_to_check:
            if not vevent_data.get(field, None):
                print "Does not have field: %s" % (field,)
                return False
        return True

from elixir import *
class Event(Entity):
    has_field('event_id', Integer, primary_key=True)

    has_field('summary', Unicode(200))
    has_field('location', Unicode(200))
    has_field('description', Unicode())
    has_field('url', String(255))

    has_field('dtstart', DateTime)
    has_field('dtend', DateTime)

    belongs_to('post', of_kind="Post", colname='post_id', inverse='events')

    using_options(tablename='a2d_event')


class HCalendarAggregatorMixin(object):
    def process_entry_hcalendar(self, post, feed, entry, posts, parsed_data):
        if not hasattr(self, "saveEvent"):
            return
        content = StringIO('<div>' +
            genshi.HTML(post.content).render('xhtml') +
            '</div>')
        hc = HCalendar(content)
        for event in hc.get_events():
            print "Received: %s" % (event,)
            self.saveEvent(**event)

    def saveEvent(self, **event):
        e = Event(**event)
        e.save()
        print e

if __name__ == "__main__":
    metadata.connect("mysql://root@localhost:3306/pyaggregator")

    from pyaggregator.aggregator import Aggregator
    from pyaggregator.elixirsupport import ElixirAggregatorMixin
    from pyaggregator.elixirsupport import Feed

    create_all()
    class MyAggregator(HCalendarAggregatorMixin, ElixirAggregatorMixin, Aggregator):
        pass
    options = {
        'verbose': True,
        'reraiseentryexceptions': True,
    }
    processor = MyAggregator(**options)
    for feed in Feed.select():
        processor.process_feed(feed)

    objectstore.flush()
