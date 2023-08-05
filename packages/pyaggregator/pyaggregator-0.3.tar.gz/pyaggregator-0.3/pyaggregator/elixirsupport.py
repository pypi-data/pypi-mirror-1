# These are example models and methods to use with the Aggregator class
#
# Copyright 2007, Neil Blakey-Milner
#
# See LICENSE file for your rights to use this code

from elixir                 import Unicode, DateTime, String, Integer
from elixir                 import Entity, has_field, using_options
from elixir                 import has_many, belongs_to, has_and_belongs_to_many
from elixir                 import objectstore
from sqlalchemy             import ForeignKey 
from datetime               import datetime

class Feed(Entity):
    has_field('feed_id', Integer, primary_key=True)

    has_field('feed_url', String(255), unique=True)

    has_field('title', Unicode(200))
    has_field('description', Unicode())
    has_field('link', String(255))

    has_field('etag', String(50))
    has_field('last_modified', DateTime)

    has_field('last_checked', DateTime)

    has_and_belongs_to_many('tags', of_kind='Tag', inverse='feeds')
    has_many('posts', of_kind='Post')

    using_options(tablename='a2d_feed')

class Tag(Entity):
    has_field('tag_id', Integer, primary_key=True)
    has_field('name', Unicode(50))

    has_and_belongs_to_many('posts', of_kind='Post', inverse='tags')
    has_and_belongs_to_many('feeds', of_kind='Feed', inverse='tags')

    using_options(tablename='a2d_tag')

class Post(Entity):
    has_field('post_id', Integer, primary_key=True)

    has_field('link', String(255))
    has_field('title', Unicode(255))
    has_field('content', Unicode())

    has_field('date_created', DateTime)
    has_field('date_modified', DateTime)

    has_field('guid', String(200), unique=True)

    has_field('author', Unicode(100))
    has_field('author_email', String(255))

    has_field('comments_url', String(255))

    has_and_belongs_to_many('tags', of_kind='Tag', inverse='posts')
    belongs_to('feed', of_kind="Feed", colname='feed_id', required=True)

    using_options(tablename='a2d_post')

class Enclosure(Entity):
    has_field('enclosure_id', Integer, primary_key=True)

    has_field('url', String(255))
    has_field('type', Unicode(255))
    has_field('size', Integer)

    has_field('duration', Integer) # in seconds

    has_field('date_created', DateTime)
    has_field('date_modified', DateTime)

    belongs_to('post', of_kind="Post", colname='post_id', inverse='enclosures')

    using_options(tablename='a2d_enclosures')

from pyaggregator.aggregator import Aggregator

class ElixirAggregatorMixin(object):
    def create_post(self, **kw):
        post = Post(**kw)
        post.save()
        objectstore.flush()
        return post

    def posts_for_guids(self, feed, guids):
        for guid in guids:
            posts = Post.select((Post.c.feed_id == feed.feed_id) & (Post.c.guid == guid))
            if not len(posts):
                continue
            yield posts[0]

    def set_tags_for_post(self, post, tags):
        post.tags = tags

    def get_or_create_tag(self, tagname):
        tags = Tag.select(Tag.c.name == tagname)
        if not tags:
            return Tag(name = tagname)
        return tags[0]

    def save_enclosure(self, **kw):
        Enclosure(**kw).save()

    def clear_enclosures_for_post(self, post):
        Enclosure.table.delete(Enclosure.c.post_id == post.post_id)
