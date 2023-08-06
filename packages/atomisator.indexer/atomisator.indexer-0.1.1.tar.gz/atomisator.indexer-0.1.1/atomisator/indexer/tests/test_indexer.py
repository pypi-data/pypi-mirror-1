import time

from atomisator.indexer import Indexer
from afpy.xap.xapindexer import start_server, stop_server
from afpy.xap.searcher import search 

def test_index():

    i = Indexer()

    entry = {'link': 'http://here',
             'summary': 'index me'}
    i(entry, [])

    # ok so now we should have something
    # to index
    start_server()
    time.sleep(0.5)
    stop_server()

    # let's check 
    assert list(search('index')) == ['http://here']

