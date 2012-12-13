# -*- coding: utf-8 *-*
from solr import SolrConnection, SolrPaginator
from optparse import OptionParser
import nltk

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki to perform calculations against")
parser.add_option("-l", "--limit", dest="limit", action="store", default=None,
                  help="Specifies the document size of the calculation set")

(options, args) = parser.parse_args()

if not options.wiki:
    raise Exception('A wiki is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

ne = []

query = ["host:'%s'" % (options.wiki), 'ns:0']

response = conn.query(' AND '.join(query), fields=['html_en','nolang_txt','html'], sort='backlinks desc', limit=100)
paginator = SolrPaginator(response)

for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        try:
            text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
            print nltk.chunk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text)))
        except UnicodeEncodeError:
            print 'Unicode problem', text
