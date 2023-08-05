from elixir import *

metadata.connect("mysql://root@localhost:3306/pyaggregator")

from pyaggregator.aggregator import Aggregator
from pyaggregator.elixirsupport import ElixirAggregatorMixin
from pyaggregator.elixirsupport import Feed

create_all()
#feed1 = Feed(feed_url="http://nxsy.org/blog/rss2.0.xml")
#feed1.save()
#objectstore.flush()

class MyAggregator(ElixirAggregatorMixin, Aggregator):
    pass


tags = {}
options = {
    'verbose': True,
    'reraiseentryexceptions': True,
}
processor = MyAggregator(**options)
for feed in Feed.select():
    processor.process_feed(feed)

objectstore.flush()
