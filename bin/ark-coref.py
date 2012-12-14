# -*- coding: utf-8 *-*
import sys
from subprocess import Popen, PIPE, STDOUT
sys.path.append(sys.path[0]+'/../nltk_contrib')

from optparse import OptionParser
from solr import SolrConnection, SolrPaginator

parser = OptionParser()
parser.add_option("-d", "--id", dest="id", action="store", default=None,
                  help="Specifies the document ID in Solr")

(options, args) = parser.parse_args()

if options.id:
    query = 'id:%s' % (options.id)
else:
    raise Exception('A wiki  or ID is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

response = conn.query(query, fields=['html_en','nolang_txt','html', 'title', 'title_en', 'id'])
paginator = SolrPaginator(response)

ARK = sys.path[0]+'/../arkref/arkref.sh'
PROPS =  sys.path[0]+'/../arkref/config/arkref.properties'
for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
        title = doc.get('title_en', doc.get('title', doc['id']))
        p = Popen([ARK, '-stdin', '-propertiesFile', PROPS], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        print p.communicate(input=text.encode('utf8'))[0]
