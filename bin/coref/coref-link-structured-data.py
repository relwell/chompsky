# -*- coding: utf-8 *-*

from optparse import OptionParser
from pymongo import MongoClient
import urllib2, json

parser = OptionParser()
parser.add_option("-u", "--apiurl", dest="api_url", action="store", default="None", # hidden for security purposes
                  help="Specifies the structured data URL end point")
parser.add_option("-H", "--host", dest="host", action="store", default="localhost",
                  help="The host of the MongoDB connection")
parser.add_option("-P", "--port", dest="port", action="store", default="27017",
                  help="The port of the MongoDB connection")
parser.add_option("-b", "--dbname", dest="dbname", action="store", default="nlp",
                  help="The database name to use")

(options, args) = parser.parse_args()

connection = MongoClient(options.host, int(options.port))
db = connection[options.dbname]

url = "%s?withType=callofduty:Character" % (options.api_url)
result = urllib2.urlopen(urllib2.Request(url, headers={'Accept':'application/json'}))
jsonstring = result.read()
characters = json.loads(jsonstring)

for character in characters:
    found = db.corefs.find({"lemmaphrase":character['schema:name']})
    if found.count() == 0:
        continue
    print "======================", character['schema:name'], "===================="
    for instance in found:
        print instance['wid']
        print "\t"+"\n\t".join([coref['phrase'] for coref in db.corefs.find({"corefid":instance['corefid']})])
    print "========================================================================="
