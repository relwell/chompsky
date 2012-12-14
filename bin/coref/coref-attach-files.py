# -*- coding: utf-8 *-*
"""
Passes raw files to Stanford CoreNLP for processing
"""

from optparse import OptionParser
import os, shutil, subprocess

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki in Solr")
parser.add_option("-p", "--poll", dest="poll", action="store", default="/tmp/nlp_raw",
                  help="The target path to poll for files")
parser.add_option("-t", "--temp", dest="temp", action="store", default="/tmp/nlp_processing",
                  help="The destination path for files being processed")
parser.add_option("-d", "--dest", dest="dest", action="store", default="/tmp/nlp_processed",
                  help="The destination path for processed files")
parser.add_option("-T", "--threads", dest="threads", action="store", default="5",
                  help="Number of threads for CoreNLP to use")
#TODO: change this path to something else
parser.add_option("-n", "--nlp-path", dest="nlppath", action="store", default="/Users/relwell/Desktop/stanford-corenlp-full-2012-11-12",
                  help="Number of threads for CoreNLP to use")

(options, args) = parser.parse_args()

LOCKFILE = 'LOCK'
lockfilepath = '%s/%s' % (options.poll, LOCKFILE)
TEMPDIR = options.temp+'/'+str(os.getpid())

if not os.path.exists(options.dest):
    os.makedirs(options.dest)

"""
Move a folder to a temp directory,
configure and call the tagger subprocess,
and delete the temp directory
"""
def attach(folder):
    args = ['java', '-cp']
    jarfiles = ['stanford-corenlp-1.3.4.jar', 'stanford-corenlp-1.3.4-models.jar', 'xom.jar', 'joda-time.jar', 'jollyday.jar']
    args.append(':'.join([options.nlppath+'/'+jarfile for jarfile in jarfiles]))
    args.append('-Xmx3g')
    args.append('edu.stanford.nlp.pipeline.StanfordCoreNLP')
    args.append('-annotators')
    args.append('tokenize,ssplit,pos,lemma,ner,parse,dcoref')
    args.append('-file')
    args.append(TEMPDIR)
    args.append('-threads')
    args.append(options.threads)
    args.append('-replaceExtension')
    args.append('-outputDirectory')
    args.append(options.dest)
    shutil.move(folder, TEMPDIR)
    subprocess.call(args)
    shutil.rmtree(TEMPDIR)

"""
Recursively iterate through the target polling folder
for unlocked, terminal folders
"""
while True:
    for folder, subs, files in os.walk(options.poll):
        if len(subs) == 0 and LOCKFILE not in files:
            attach(folder)
