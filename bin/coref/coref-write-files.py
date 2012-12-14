# -*- coding: utf-8 *-*
"""
Writes Solr documents to their own flat files as part of a coref resolution (and more) pipeline
Throughput on this one is pretty fast, because it's just writing raw text
"""

from optparse import OptionParser
from solr import SolrConnection, SolrPaginator
from time import sleep
import os

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki in Solr")
parser.add_option("-d", "--dest", dest="dest", action="store", default="/tmp/nlp_raw",
                  help="The destination path of files")

(options, args) = parser.parse_args()

if options.wiki:
    query = 'host:%s' % (options.wiki)
else:
    raise Exception('A wiki is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

response = conn.query(query, fields=['html_en','nolang_txt','html', 'title', 'title_en', 'id'], rows=100)
paginator = SolrPaginator(response)

def initialize_dir(page):
    paths = [options.dest, options.wiki, str(page)]
    fullpath = ''
    for path in paths:
        fullpath += path + '/'
        if not os.path.exists(fullpath):
            os.mkdir(fullpath)
    return fullpath

for page in paginator.page_range:
    pagedir = initialize_dir(page)
    lockfilepath = pagedir+'/LOCK'
    with open(lockfilepath, 'w') as lockfile:
        for doc in paginator.page(page).object_list:
            text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
            title = doc.get('title_en', doc.get('title', doc['id']))
            f = open('%s/%s.raw' % (pagedir, doc['id']), 'w')
            f.write("%s\n%s" % (title.encode('utf8'), text.encode('utf8')))
            f.close()
    os.remove(lockfilepath)
