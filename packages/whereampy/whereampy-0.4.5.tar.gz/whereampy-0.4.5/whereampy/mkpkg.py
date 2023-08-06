#!/usr/bin/env python
import os
import sys
import optparse
from pkg_resources import resource_string

SEP = os.path.sep

def logger(verbosity, out=sys.stderr):
    def write(msg, *args):
        out.write((msg % args)+"\n")

    def log(v, msg, *args):
        if v <= verbosity:
            write(msg, *args)
        if v <= 0:
            sys.exit(1)

    def debug(msg, *args):
        log(3, msg, *args)

    def info(msg, *args):
        log(2, msg, *args)

    def warn(msg, *args):
        log(1, msg, *args)

    def error(msg, *args):
        log(0, msg, *args)

    if verbosity > 3:
        debug('Maximum verbosity is 3')

    return log, debug, info, warn, error

def parse(args):
    p = optparse.OptionParser(usage='%prog [OPTIONS] DIRECTORY')
    p.add_option('-v', '--verbose', action='count', default=0)
    p.add_option('-s', '--setup', action='store_true', default=False,
            help='create setup.py in the first created directory instead of'
                 ' __init__.py file')
    p.add_option('-p', '--parents', action='store_true', default=False,
            help='create parent directories as needed')
    p.add_option('-e', '--existing', action='store_true', default=False,
            help='create __init__.py files in existing directories')
    p.add_option('-l', '--last-only', action='store_true', default=False,
            help='only create __init__.py files in the last directory')

    options, args = p.parse_args(args)

    if len(args) > 1:
        p.error('Only one argument (DIRECTORY) allowed.')
    elif len(args) < 1:
        p.error('Missing required DIRECTORY argument.')

    return options, args[0]

def makesetup():
    template = resource_string(__name__, 'setup.py.template')
    target = open('setup.py', 'w')
    target.write(template)
    target.close()

def makepkg(dir, setup, existing, last_only, verbosity=0):
    log, debug, info, warn, error = logger(verbosity)
    debug('Options: setup=%s, existing=%s, last_only=%s, verbosity=%s',
            setup, existing, last_only, verbosity)
    if dir[0] == SEP:
        debug('Changing to root directory')
        os.chdir(SEP)

    parts = dir.split(SEP)
    numparts = len(parts)
    first_created = True
    for i, part in enumerate(parts):
        if not part: continue
        info('Making directory %s', part)
        if os.path.exists(part):
            warn('%s exists, skipping', part)
            created = False
        else:
            os.mkdir(part)
            created = True
        debug('Changing to directory %s', part)
        os.chdir(part)

        last = i == (numparts - 1)
        existing_ok = created or existing
        last_ok = (last and last_only) or (last_only == False)
        if setup and (created and first_created):
            info('Creating %s%ssetup.py', part, SEP)
            makesetup()
            first_created = False
        elif existing_ok and last_ok:
            info('Creating __init__.py file in %s', part)
            f = open('__init__.py', 'w')
            f.close()
        else:
            debug('Skipping creation of __init__.py or setup.py')

def main(args=None):
    if not args:
        args = sys.argv[1:]
    options, dir = parse(args)
    makepkg(dir, options.setup, options.existing, options.last_only,
            options.verbose)
