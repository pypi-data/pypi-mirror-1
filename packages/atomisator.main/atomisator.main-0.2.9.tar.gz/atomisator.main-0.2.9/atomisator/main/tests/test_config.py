from atomisator.main.config import AtomisatorConfig
import os
from nose.tools import *

cfg = os.path.join(os.path.dirname(__file__), 'test.cfg')

def test_config():
    parser = AtomisatorConfig(cfg)
    s = parser.sources 
    waited = [('rss', ('gdigg.xml',)), ('rss', ('gtarek.xml',)), 
              ('rss', ('gpp.xml',)), ('rss', ('gdigg.xml',)), 
              ('rss', ('gtarek.xml',)), ('rss', ('gpp.xml',))]

    assert_equals(s, waited)
    parser.sources = (('rss', ('ok.xml',)),)
    assert_equals(parser.sources, [('rss', ('ok.xml',))])

    assert_equals(parser.database, 'sqlite:///gatomisator.db') 
    parser.database = 'sqlite://here'
    assert_equals(parser.database, 'sqlite://here')    

    assert_equals(parser.title, 'meta') 
    parser.title = 'here'
    assert_equals(parser.title, 'here')    

    assert_equals(parser.description, 'My feed') 
    parser.description = 'My feed 2'
    assert_equals(parser.description, 'My feed 2')    

    assert_equals(parser.timeout, '5') 
    parser.timeout = '7'
    assert_equals(parser.timeout, '7')

    assert_equals(parser.link, 'http://link') 
    parser.link = 'http://link'
    assert_equals(parser.link, 'http://link')

    assert_equals(parser.file, 'gatomisator.xml') 
    parser.file = 'op.xml'
    assert_equals(parser.file, 'op.xml')

