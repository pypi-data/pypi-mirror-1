#!/usr/bin/env python

from elixir import *
class Generator(Entity):
    has_field('generator', Unicode(200))

    belongs_to('feed', of_kind="Feed", colname='feed_id', inverse='generator')

    using_options(tablename='a2d_generator')


class GeneratorAggregatorMixin(object):
    def process_feed_generator(self, feed, parsed_data):
        if not hasattr(parsed_data.feed, 'generator'):
            return
        self.setGeneratorForFeed(feed = feed, generator = parsed_data.feed.generator)

    def setGeneratorForFeed(self, feed, generator):
        g = Generator.get_by(feed=feed)
        if not g:
            g = Generator()
        g.feed = feed
        g.generator = generator
        g.save()

if __name__ == "__main__":
    metadata.connect("mysql://root@localhost:3306/pyaggregator")

    from pyaggregator.aggregator import Aggregator
    from pyaggregator.elixirsupport import ElixirAggregatorMixin
    from pyaggregator.elixirsupport import Feed

    create_all()
    class MyAggregator(GeneratorAggregatorMixin, ElixirAggregatorMixin, Aggregator):
        pass
    options = {
        'verbose': True,
        'reraiseentryexceptions': True,
    }
    processor = MyAggregator(**options)
    for feed in Feed.select():
        processor.process_feed(feed)

    objectstore.flush()
