import os
import sys
from optparse import OptionParser

from whereampy.main import whereampy

def parse(inargs):
    parser = OptionParser(usage='usage: %prog [options] [path]...')
    parser.add_option('-s', '--self', action='store_true', default=False,
            help='check path of this script')
    options, args = parser.parse_args(inargs)

    args.pop(0) # Remove sys.argv[0]

    if options.self:
        args.append(os.getcwd())

    if len(args) == 0:
        args.append(os.environ['PWD'])

    return options, args

def main():
    options, args = parse(sys.argv)

    for path in args:
        print path
        for desc in whereampy(path):
            print ' ', desc
        print
