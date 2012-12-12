# -*- coding: utf-8 *-*
"""
Performs sentiment analysis on talk pages for a given wiki
"""

from solr import SolrConnection, SolrPaginator
from pattern.text.en.parser import sentiment
from optparse import OptionParser
from numpy import average, std, var

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki to perform calculations against")
parser.add_option("-d", "--start-date", dest="start_date", action="store", default=None,
                  help="Specifies the start date for articles to query (in format YYYY-MM-DD)")
parser.add_option("-e", "--end-date", dest="end_date", action="store", default=None,
                  help="Specifies the end date for articles to query (in format YYYY-MM-DD)")
parser.add_option("-n", "--namespace", dest="namespace", default=1, #NS_TALK
                  help="Specifies the namespace to use (blog namespace by default)")

(options, args) = parser.parse_args()

if not options.wiki:
    raise Exception('A wiki is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

query = ["host:'%s'" % (options.wiki)]

query += ['ns:%d ' % (int(options.namespace))]

if options.start_date or options.end_date:
    start = options.start_date + 'T00:00:00.000Z' if options.start_date else '*'
    end = options.end_date + 'T00:00:00.000Z' if options.end_date else '*'
    query += ['created:[%s TO %s]' % (start, end)]

response = conn.query(' AND '.join(query), fields=['html_en','nolang_txt','html'])
paginator = SolrPaginator(response)

print paginator.count, 'results to chomp through...'

polarities, subjectivities = [], []

for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        sent = sentiment.sentiment(doc.get('html_en', doc.get('nolang_txt', doc.get('html'))))
        if ( sent == (0,0)):
            continue
        polarities.append(sent[0])
        subjectivities.append(sent[1])
    if page % int(paginator.num_pages/10) == 0:
        print "========","On page", page, "of", paginator.num_pages, "======="
        print
        print "Polarity:"
        print "\tAverage:", average(polarities)
        print "\tStdDev:", std(polarities)
        print "\tVariance:", var(polarities)
        print "Subjectivity:"
        print "\tAverage:", average(subjectivities)
        print "\tStdDev:", std(subjectivities)
        print "\tVariance:", var(subjectivities)
        print
        print "==================================="
        print

print "In general, discourse is",
print "positive" if average(polarities) > 0 else "negative",
print "and subjective" if average(subjectivities) >= 0.5  else "and objective"
print
