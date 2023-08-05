#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    from elixir import metadata, objectstore
    metadata.connect("mysql://root@localhost:3306/pyaggregator")

    from pyaggregator.aggregator import Aggregator
    from pyaggregator.elixirsupport import ElixirAggregatorMixin
    from pyaggregator.elixirsupport import Feed

    Feed.table.delete()
    for feed_url in sys.stdin:
        feed_url = feed_url.strip()
        Feed(feed_url = feed_url).save()

    objectstore.flush()
