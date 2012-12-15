# -*- coding: utf-8 *-*
import sys
sys.path.append(sys.path[0]+'/../nltk_contrib')

from nltk_contrib.readability.readabilitytests import ReadabilityTool
from optparse import OptionParser
from solr import SolrConnection, SolrPaginator

parser = OptionParser()
parser.add_option("-d", "--id", dest="id", action="store", default=None,
                  help="Specifies the document ID in Solr")
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki to perform calculations against")

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

tool = ReadabilityTool(lang='eng')

for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
        title = doc.get('title_en', doc.get('title', doc['id']))
        print "=======", title, "======="
        tool.getReportAll(text.encode('utf8'))
        print "====================================="
