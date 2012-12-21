# -*- coding: utf-8 *-*
"""
Sends XML output from Stanford CoreNLP and stores it in MongoDB
"""

from optparse import OptionParser
from pymongo import MongoClient
from xml.etree import ElementTree
import os, shutil

parser = OptionParser()
parser.add_option("-d", "--dir", dest="dir", action="store", default="None",
                  help="The location of the XML files")
parser.add_option("-H", "--host", dest="host", action="store", default="localhost",
                  help="The host of the MongoDB connection")
parser.add_option("-p", "--port", dest="port", action="store", default="27017",
                  help="The port of the MongoDB connection")
parser.add_option("-b", "--dbname", dest="dbname", action="store", default="nlp",
                  help="The database name to use")
parser.add_option("-x", "--delete", dest="delete", action="store", default=True,
                  help="Whether to delete the folder when we are done with it")

(options, args) = parser.parse_args()

if not os.path.exists(options.dir):
    raise Exception("The specified path does not exist")

connection = MongoClient(options.host, int(options.port))
db = connection[options.dbname]

def transform(folder, xmlfile):
    path = folder + '/' + xmlfile
    tree = ElementTree.parse(path)
    root = tree.getroot()
    corefs = root.iter('coreference')
    coreftransforms = []
    corefcount = 1
    for coref in corefs:
        mentions = coref.findall('.//mention')
        docid = os.path.splitext(xmlfile)[0]
        corefid = docid+'_'+str(corefcount)
        wid, pageid = docid.split('_')
        coreftransform = \
              [\
                {  'doc_id' : docid, \
                   'wid' : wid, \
                   'pageid' : pageid, \
                   'corefid' : corefid, \
                   'phrase' :' '.join([root.find('.//sentence[@id="%s"]//token[@id="%s"]//word' \
                                                % (mention.find('.//sentence').text, val)).text  \
                                        for val in range(int(mention.find('start').text), int(mention.find('end').text))\
                                    ]), \
                  'representative' : mention.attrib.get('representative', False), \
                  'lemmaphrase' : ' '.join([root.find('.//sentence[@id="%s"]//token[@id="%s"]//lemma' \
                                                % (mention.find('.//sentence').text, val)).text  \
                                        for val in range(int(mention.find('start').text), int(mention.find('end').text))\
                                    ]), \
                  'head' : root.find('.//sentence[@id="%s"]//token[@id="%s"]//word' \
                                          % (mention.find('.//sentence').text, mention.find('.//head').text) \
                                    ).text, \
                  'lemmahead' : root.find('.//sentence[@id="%s"]//token[@id="%s"]//lemma' \
                                          % (mention.find('.//sentence').text, mention.find('.//head').text) \
                                    ).text, \
                  'phrasepos' : [root.find('.//sentence[@id="%s"]//token[@id="%s"]//POS' \
                                                % (mention.find('.//sentence').text, val)).text  \
                                        for val in range(int(mention.find('start').text), int(mention.find('end').text))\
                                    ], \
                  'headpos' : root.find('.//sentence[@id="%s"]//token[@id="%s"]//POS' \
                                          % (mention.find('.//sentence').text, mention.find('.//head').text) \
                                    ).text, \
                  'ner' : [root.find('.//sentence[@id="%s"]//token[@id="%s"]//NER' \
                                                % (mention.find('.//sentence').text, val)).text  \
                                        for val in range(int(mention.find('start').text), int(mention.find('end').text))\
                                    ], \
                  'headner' : root.find('.//sentence[@id="%s"]//token[@id="%s"]//NER' \
                                          % (mention.find('.//sentence').text, mention.find('.//head').text) \
                                    ).text,
                } \
              for mention in mentions]
        coreftransforms += coreftransform
        corefcount += 1
    if len(coreftransforms) > 0:
        db.corefs.insert(coreftransforms)

for folder, subs, files in os.walk(options.dir):
    for xmlfile in files:
        try:
            transform(folder, xmlfile)
        except:
            pass
if options.delete:
    shutil.rmtree(options.dir)
