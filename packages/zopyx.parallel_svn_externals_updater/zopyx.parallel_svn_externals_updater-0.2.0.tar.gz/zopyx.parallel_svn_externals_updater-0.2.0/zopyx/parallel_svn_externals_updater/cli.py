##########################################################################
# zopyx.parallel_svn_externals_updater
# (C) 2008, ZOPYX Ltd. & Co. KG, D-72070 Tuebingen, Germany
##########################################################################

"""
Parallel update of svn:externals within a SVN checkout
"""

import os
import re
import sys
import commands
import processing 

prop_on_regex = re.compile("Properties on '(.*?)'")

def log(s):
    print >>sys.stdout, s

def find_externals(dirname, options):
    """ Returns a list with directory names (relative to 'dirname')
        that contain svn:externals.
    """

    if options.verbose:
        log('Phase 1: %s' % dirname)
    
    # ATT portable? Better using the 'py' module?
    st, output = commands.getstatusoutput('svn pl -R %s' % dirname)

    dirs_with_externals = list()
    current_dir = None
    for line in output.split('\n'):
        mo = prop_on_regex.match(line)
        if mo:
            current_dir = mo.group(1)
        else:
            if 'svn:external' in line:
                if options.verbose:
                    log('Directory with externals: %s' % current_dir)
                dirs_with_externals.append(current_dir)

    return dirs_with_externals


def expand_externals(dirnames, options):
    """ Returns a list of directory names managed through svn:externals """

    if options.verbose:
        log('Phase 2: %s' % ', '.join(dirnames))

    result = dict()
    for dirname in dirnames:
        result[dirname] = list()
        st, output =  commands.getstatusoutput('svn pg svn:externals %s' % dirname)
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                continue
            if line:
                module, url = line.split(' ', 1)
                managed_dir = os.path.join(dirname, module)
                if options.verbose:
                    log('Directory managed through svn:externals: %s' % managed_dir)
                result[dirname].append(managed_dir)

    return result


def recurse_externals(dirnames, options):
    for dir_list in dirnames.values():
        for directory in dir_list:
            externals = find_externals(directory, options)
            if not externals:
                continue
            externals = expand_externals(externals, options)
            if externals and externals.values() != [[]]:
                dirnames.update(recurse_externals(externals, options))
    return dirnames


def worker(dirname):
    st, output = commands.getstatusoutput('svn update %s' % dirname)
#    if options.verbose:
#        print output
    return st

def update_externals(data, options):

    if options.verbose:
        log('Phase 3')

    data = [(k, v) for k,v in data.items()]
    data.sort()
    for (base_dir, dirs) in data:
        if options.verbose:
            log('Processing svn:externals for %s' % base_dir)
        pool = processing.Pool(options.pool_size)
        result = pool.mapAsync(worker, dirs)
        result.get(timeout=999)


def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      default=False, help='verbose on')
    parser.add_option('-r', '--recursive', dest='recursive', action='store_true',
                      default=False, help='Recursive update')
    parser.add_option('-p', '--pool-size', dest='pool_size', action='store',
                      type='int',
                      default=10, help='Number of parallel update operations')

    (options, args) = parser.parse_args()

    if len(args) == 0:
        raise ValueError('No SVN checkout directory specified')
    elif len(args) > 1:
        raise ValueError('More than one SVN checkout directry specified')

    dirnames = find_externals(args[0], options)
    dirnames = expand_externals(dirnames, options)
    if options.recursive:
        dirnames = recurse_externals(dirnames, options)
    update_externals(dirnames, options)

if __name__ == '__main__':
    main()
