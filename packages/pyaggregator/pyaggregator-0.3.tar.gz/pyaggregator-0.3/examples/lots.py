#!/usr/bin/env python

from generator import GeneratorAggregatorMixin
from hcalendar import HCalendarAggregatorMixin
from pylucene import PyLuceneAggregatorMixin, IndexWriter, StandardAnalyzer
from links import OutgoingAggregatorMixin

if __name__ == "__main__":
    from elixir import metadata, objectstore
    metadata.connect("mysql://root@localhost:3306/pyaggregator")

    from pyaggregator.aggregator import Aggregator
    from pyaggregator.elixirsupport import ElixirAggregatorMixin
    from pyaggregator.elixirsupport import Feed

    indexDir = '/tmp/foo'
    writer = IndexWriter(indexDir, StandardAnalyzer(), True)
    class LotsAggregator(OutgoingAggregatorMixin, PyLuceneAggregatorMixin, HCalendarAggregatorMixin, GeneratorAggregatorMixin, ElixirAggregatorMixin, Aggregator):
        writer = writer
    options = {
        'verbose': True,
        'reraiseentryexceptions': True,
    }
    processor = LotsAggregator(**options)
    for feed in Feed.select():
        processor.process_feed(feed)

    writer.optimize()
    writer.close()

    objectstore.flush()
