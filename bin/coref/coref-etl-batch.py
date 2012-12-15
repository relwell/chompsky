# -*- coding: utf-8 *-*
"""
Attaches our ETL script to the appropriate directory

This assumes a different directory structure than we currently have
"""

from optparse import OptionParser
from subprocess import Popen
from time import sleep
import os, shutil

parser = OptionParser()
parser.add_option("-p", "--poll", dest="poll", action="store", default="/tmp/nlp_processed",
                  help="The target path to poll for files")
parser.add_option("-T", "--threads", dest="threads", action="store", default="5",
                  help="Number of subprocessess to open")
parser.add_option("-H", "--host", dest="host", action="store", default="localhost",
                  help="The host of the MongoDB connection")
parser.add_option("-P", "--port", dest="port", action="store", default="27017",
                  help="The port of the MongoDB connection")
parser.add_option("-b", "--dbname", dest="dbname", action="store", default="nlp",
                  help="The database name to use")
parser.add_option("-x", "--delete", dest="delete", action="store", default=False,
                  help="Whether to delete the folder when we are done with it")
parser.add_option("-t", "--transformpath", dest="transformpath", action="store", default="/Users/relwell/wikia-nlp/coref/",
                  help="The path the ETL script is located at") #TODO: change default path


(options, args) = parser.parse_args()


procs = []

def clear_finished_processes(procs):
    newprocs = []
    for dirname in procs.keys:
        if Popen.poll(procs[dirname]) == None:
            newprocs[dirname] = procs[dirname]
        elif options.delete:
            shutil.rmtree(dirname)
    return newprocs

def spawn_process(folder):
    args = [options.transformpath+'/coref-transform-xml.py', '--host='+options.host, '--port='+options.port, '--dbname='+options.dbname, '--dirname='+folder]
    print args
    return Popen(args)


while True:
    dirs = os.listdir(options.poll)
    if len(dirs) == 0:
        continue
    while len(procs) < options.threads:
        folder = dirs.pop()
        procs[folder] = spawn_process(options.poll + '/' + folder)
        procs = clear_finished_processes(procs)
    sleep(1)
