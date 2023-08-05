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

def flatten(elem, include_tail=0):
    text = elem.text or ""
    for e in elem:
        text += flatten(e, 1)
        if include_tail and elem.tail:
            text += elem.tail
    return text

import genshi
from PyLucene import IndexWriter, StandardAnalyzer, Document, Field

class PyLuceneAggregatorMixin(object):
    def process_entry_lucene(self, post, feed, entry, posts, parsed_data):
        if not hasattr(self, 'writer'):
            return

        if not self.writer:
            return

        content = StringIO('<div>' +
            genshi.HTML(post.content).render('xhtml') +
            '</div>')
        e = ET.ElementTree()
        e.parse(content)
        e = e.getroot()
        text = flatten(e)
        doc = Document()
        doc.add(Field("id", str(post.post_id), Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("title", post.title, Field.Store.YES, Field.Index.TOKENIZED))
        doc.add(Field("contents", text, Field.Store.NO, Field.Index.TOKENIZED))
        self.writer.addDocument(doc)

if __name__ == "__main__":
    from elixir import metadata, objectstore
    metadata.connect("mysql://root@localhost:3306/pyaggregator")

    from pyaggregator.aggregator import Aggregator
    from pyaggregator.elixirsupport import ElixirAggregatorMixin
    from pyaggregator.elixirsupport import Feed

    indexDir = '/tmp/foo'
    writer = IndexWriter(indexDir, StandardAnalyzer(), True)
    class MyAggregator(PyLuceneAggregatorMixin, ElixirAggregatorMixin, Aggregator):
        writer = writer
    options = {
        'verbose': True,
        'reraiseentryexceptions': True,
    }
    processor = MyAggregator(**options)
    for feed in Feed.select():
        processor.process_feed(feed)

    writer.optimize()
    writer.close()

    objectstore.flush()
