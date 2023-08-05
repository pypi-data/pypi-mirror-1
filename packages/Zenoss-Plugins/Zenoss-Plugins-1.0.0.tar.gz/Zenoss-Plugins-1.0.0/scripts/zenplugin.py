#!/bin/env python

###############################################################################
#
#   Copyright (c) 2006 Zenoss, Inc. all rights reserved.
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License.
#
###############################################################################

#
# Zenoss Plugin Program
#
# See __usage__ for an explanation of runtime arguments.
#
# -Christopher Blunck <chris@swcomplete.com>
#

import sys, getopt, os

__author__ = 'Christopher Blunck'
__email__ = 'chris@swcomplete.com'

__doc__ = '''
Runs the requested plugin and reports the outcome on stdout.
'''

__usage__ = '''
Collects information using a platform specific plugin.

Template:
  python $0 [options] plugin [arguments] [keywords]

Options:
  --list-plugins:      List supported plugins
  --list-platforms:    List supported platforms
  --detect-platform:   Report the platform python is running under

Example:
  python $0 mem

'''

# return codes 
OK = 0
ERROR = 1

# python constants
TRUE = 1
FALSE = 0

# set DEBUG to TRUE to see stack traces when an error occurs
DEBUG = FALSE


def usage():
    print __usage__


def main():
    # arguments are definitely required
    if len(sys.argv) < 2:
        usage()
        sys.exit(ERROR)

    # determine the system platform
    platform = sys.platform

    # parse those command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   'h', ["help", 
                                         "list-plugins", 
                                         "list-platforms",
                                         "detect-platform"])
    except getopt, GetoptError:
        usage()
        sys.exit(ERROR)

    # parse the command line arguments and handle them
    for o, a in opts:
        # --help displays usage
        if o in ('-h', '--help'):
            usage()
            sys.exit(ERROR)

        # --list-plugins displays a list of plugins for the platform
        if o in ('--list-plugins'):
            listPlugins(platform)
            sys.exit(OK)

        # --list-platforms displays a list of platforms that are implemented
        if o in ('--list-platforms'):
            listPlatforms()
            sys.exit(OK)

        # --detect-platform prints out the detected platform
        if o in ('--detect-platform'):
            print platform
            sys.exit(OK)
            


    # check if the plugin exists
    plugin = args[0]
    if not collectorExists(platform, plugin):
        m = "collector '%s' doesn't exist on platform '%s'" % (plugin, platform)
        print m
        sys.exit(ERROR)

    # create a collector for the plugin
    collector = createCollector(platform, plugin, args[1:], {})

    # use the collector to read the data
    try:
        collector.collect()
        out(plugin, collector)
    except:
        message = sys.exc_info()[0]
        sys.stdout.write('%s;|' % message)

        if DEBUG:
            import traceback
            traceback.print_exc()

        sys.exit(ERROR)


def getPlatformModule(platform):
    '''returns the module containing plugins for the platform requested,
    or None if the platform is not implemented.'''

    mod = None
    try:
        mod = getattr(__import__('zenoss.plugins.%s' % platform), 'plugins')
        mod = getattr(mod, platform, None)
    except:
        pass
    
    return mod


def platformExists(platform):
    '''returns true if a module is defined for the platform provided'''

    return getPlatformModule(platform) != None


def listPlatforms():
    '''lists the platforms that supported'''
    
    print 'the following platforms and modules are supported:'

    # determine where to look for the platform modules
    mod = __import__('zenoss.plugins')
    moduleDir = mod.__path__[0]
    for file in os.listdir(moduleDir):
        name, ext = os.path.splitext(file)

        # ignore data files, compiled modules, etc
        if ext != '.py':
            continue

        # try to import the module and get the platform modules from it
        mod = getattr(__import__('zenoss.plugins.%s' % name), name)
        nameMap = getattr(mod, 'COLLECTOR_NAMES', {})
        keys = nameMap.keys()
        keys.sort()

        # if the platform has plugins defined print them out
        if len(keys) > 0:
            sys.stdout.write('  %s:  ' % name)
            for plugin in keys:
                sys.stdout.write('%s ' % plugin)

            sys.stdout.write('\n')


def listPlugins(platform):
    '''lists the plugins available for the requested platform'''

    if not platformExists(platform):
        print "platform '%s' is not implemented.  no plugins exists" % platform
        
    map = getNameMap(platform)
    print "platform '%s' supports the following plugins:" % platform
    for plugin in map.keys():
        print '  %s' % plugin 
        

def getNameMap(platform):
    '''returns the name map for the requested platform.  the name map
    provides a mapping between plugin names and class names.'''

    return getattr(getPlatformModule(platform), 'COLLECTOR_NAMES', {})
    

def collectorExists(platform, plugin):
    '''returns true if the collector exists, or false if it does not.  a
    collector may not exist if the platform that this requested is not
    supported.  or, a collector may not exist if the platform exists
    but the plugin is not defined (a class name is not provided in
    COLLECTOR_NAMES).  or lastly, a collector may not exist if the
    platform exists, a map is defined in COLLECTOR_NAMES, but the
    mapped class does not exist in the platform module (this indicates
    a programming error).'''

    # is the platform supported?
    if not platformExists(platform):
        return FALSE

    # does the plugin exist for the platform?
    nameMap = getNameMap(platform)
    if not nameMap.has_key(plugin):
        return FALSE
    
    # does the class exist in the platform's module?
    mod = getPlatformModule(platform)
    return hasattr(mod, nameMap[plugin])



def createCollector(platform, plugin, args, kwargs):
    '''locates the plugin for the platform requested and constructs it
    using the args and kwargs provided.  the resulting collector is
    returned.'''

    module = getPlatformModule(platform)
    nameMap = getattr(module, 'COLLECTOR_NAMES', {})
    clazz = getattr(module, nameMap[plugin])
    collector = clazz(*args, **kwargs)

    return collector


def out(plugin, collector):
    '''outputs the various name value pairs to a single line'''

    # collection succeeded, so output the values
    output = '%s OK;|' % plugin.upper()
    for pos,key in enumerate(collector.map.keys()):
        value = collector.map[key]

        if pos == 0:
            output += '%s=%s' % (key, value)
        else:
            output += ' %s=%s' % (key, value)            


    sys.stdout.write(output)
    

if __name__ == '__main__':
    main()
