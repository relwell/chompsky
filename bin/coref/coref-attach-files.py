# -*- coding: utf-8 *-*
"""
Writes Solr documents to their own flat files as part of a coref resolution (and more) pipeline
"""

from optparse import OptionParser
from time import sleep
import os

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki in Solr")
parser.add_option("-p", "--poll", dest="dest", action="store", default="/tmp/flat_files",
                  help="The target path to poll for files")
parser.add_option("-d", "--dest", dest="dest", action="store", default="/tmp/processed_files",
                  help="The destination path for processed files")

(options, args) = parser.parse_args()

lockfilepath = '%s/attacher.LOCK' % (options.poll)

while True:
    listed = os.listdir(options.poll)
    if len(listed) > 0 and 'attacher.LOCK' not in listed:
        lockfile = open(lockfilepath, 'w')
        lockfile.write('')
        lockfile.close()
        # move folder someplace else based guid so multiple pollers can eventually be dispatched
        os.remove(lockfilepath)
        # call stanford stuff
    sleep(10)
