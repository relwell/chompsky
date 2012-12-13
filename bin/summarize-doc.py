# -*- coding: utf-8 *-*
import sys
sys.path.append(sys.path[0]+'/../summarize')

from summarize import SimpleSummarizer
from optparse import OptionParser
from solr import SolrConnection, SolrPaginator

parser = OptionParser()
parser.add_option("-d", "--id", dest="id", action="store", default=None,
                  help="Specifies the document ID in Solr")
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki to perform calculations against")
parser.add_option("-n", "--sents", dest="num_sents", action="store", default=5,
                  help="Specifies the number of sentences to write")

(options, args) = parser.parse_args()

if options.id:
    query = 'id:%s' % (options.id)
elif options.wiki:
    query = "host:'%s' AND ns:0" % (options.wiki)
else:
    raise Exception('A wiki  or ID is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

response = conn.query(query, fields=['html_en','nolang_txt','html', 'title', 'title_en', 'id'])
paginator = SolrPaginator(response)

summarizer = SimpleSummarizer()

for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
        title = doc.get('title_en', doc.get('title', doc['id']))
        summed = summarizer.get_summarized(text, options.num_sents)
        print "\t\t=======", title, "======="
        print "\t"+"\n\t".join([sent for sent in summed if not sent.startswith('Contents')])
        print "\t\t====================================="
