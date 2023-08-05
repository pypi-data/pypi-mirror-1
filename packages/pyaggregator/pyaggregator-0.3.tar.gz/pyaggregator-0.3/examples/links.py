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

def flatten(elem, include_tail=0):
    text = elem.text or ""
    for e in elem:
        text += flatten(e, 1)
        if include_tail and elem.tail:
            text += elem.tail
    return text

class OutgoingFind(object):
    def __init__(self, content):
        self.content = content

    def get_outgoing(self):
        tree = ET.ElementTree()
        tree.parse(self.content)
        for elem in tree.findall(".//a"):
            if elem.get('rel'):
                if 'nofollow' in elem.get('rel'):
                    continue
            if not elem.get('href'):
                continue
            description = elem.get('title', None)
            if not description:
                description = flatten(elem)
            yield elem.get('href'), description

import genshi

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from elixir import *
class Outgoing(Entity):
    has_field('outgoing_id', Integer, primary_key=True)

    has_field('url', String(255))
    has_field('description', Unicode())
    belongs_to('post', of_kind="Post", colname='post_id', inverse='outgoing_links')

    using_options(tablename='a2d_outgoing')

class OutgoingAggregatorMixin(object):
    def process_entry_outgoing(self, post, feed, entry, posts, parsed_data):
        content = StringIO('<div>' +
            genshi.HTML(post.content).render('xhtml') +
            '</div>')
        finder = OutgoingFind(content)
        self.clearOutgoingForPost(post)
        for link, description in finder.get_outgoing():
            print "Received: %s - %s" % (link, description)
            self.setOutgoingForPost(post, link, description)

    def clearOutgoingForPost(self, post):
        Outgoing.table.delete(Outgoing.c.post_id == post.post_id)

    def setOutgoingForPost(self, post, link, description):
        Outgoing(post = post, url = link, description = description).save()

if __name__ == "__main__":
    metadata.connect("mysql://root@localhost:3306/pyaggregator")

    from pyaggregator.aggregator import Aggregator
    from pyaggregator.elixirsupport import ElixirAggregatorMixin
    from pyaggregator.elixirsupport import Feed

    create_all()
    class MyAggregator(OutgoingAggregatorMixin, ElixirAggregatorMixin, Aggregator):
        pass
    options = {
        'verbose': True,
        'reraiseentryexceptions': True,
    }
    processor = MyAggregator(**options)
    for feed in Feed.select():
        processor.process_feed(feed)

    objectstore.flush()
