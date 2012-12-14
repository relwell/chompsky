# -*- coding: utf-8 *-*
"""
Writes Solr documents to their own flat files as part of a coref resolution (and more) pipeline
"""

from optparse import OptionParser
from solr import SolrConnection, SolrPaginator
from time import sleep
import os

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki in Solr")
parser.add_option("-d", "--dest", dest="dest", action="store", default="/tmp/flat_files",
                  help="The destination path of files")

(options, args) = parser.parse_args()

if options.wiki:
    query = 'host:%s' % (options.wiki)
else:
    raise Exception('A wiki is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

response = conn.query(query, fields=['html_en','nolang_txt','html', 'title', 'title_en', 'id'])
paginator = SolrPaginator(response)

for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
        title = doc.get('title_en', doc.get('title', doc['id']))
        while 'attacher.LOCK' in os.listdir(options.dest):
            sleep(0.5)
        f = open('%s/%s' % (options.dest, doc['id']), 'w')
        f.write("%s\n%s" % (title, text))
        f.close()
