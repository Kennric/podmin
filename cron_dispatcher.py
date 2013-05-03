import os
from optparse import OptionParser
from django.core.management import setup_environ
import settings

setup_environ(settings) 

usage = "usage: %prog -a ACTION | --action=ACTION"
parser = OptionParser(usage)

parser.add_option('-a', '--action', dest='action', metavar='ACTION',
                      help="The Action to perform")

(options, args) = parser.parse_args()

if not options.action:
  parser.error("An Action must be specified")

exec("from cronJobs import " + options.action)

