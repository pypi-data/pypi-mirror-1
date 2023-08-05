#!/usr/bin/env python
from xmlmodel import *
from datetime import datetime

class rss( XMLModel ):
    class XMLAttrs:
        version = '2.0'
    
    class channel( XMLNode ):
        title = XMLValue('test')
        description = XMLValue('something')
        link = XMLValue('http://here')
        lastBuildDate = XMLDateTime( format = "%a, %d %b %Y %H:%M:%S EST" )
        generator = XMLValue()
        docs = XMLValue()
        
        class item( XMLNodeList ):
            title = XMLValue()
            link = XMLValue()
            description = XMLValue()
            category = XMLList()
            pubDate = XMLDateTime( format = "%a, %d %b %Y %H:%M:%S EST" )

feed = rss()

feed.channel.title = 'Latest Headlines'
feed.channel.description = 'Most Recent Headlines'
feed.channel.generator = 'XMLModel 0.1a'
feed.channel.lastBuildDate = datetime( 2006, 5, 10, 8, 24, 30 )

item = feed.channel.item.new()
item.title = 'foo'
item.link = 'http://foo'
item.description = 'foo bar'
item.category.append( 'foo' )
item.category.append( 'bar' )
item.pubDate = datetime( 2005, 1, 2, 3, 4, 5 )

item = feed.channel.item.new()
item.title = 'bar'
item.link = 'http://bar'
item.description = 'bar baz'
item.category.append( 'bar' )
item.category.append( 'baz' )
item.pubDate = datetime( 2006, 2, 3, 4, 5, 6 )

print feed
    
