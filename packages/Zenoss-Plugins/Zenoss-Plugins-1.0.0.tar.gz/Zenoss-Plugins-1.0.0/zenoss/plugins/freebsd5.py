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


# mappings of collector names (from the command line) to classes
COLLECTOR_NAMES = {'cpu' : 'CPUCollector',
                   'mem' : 'MemoryCollector',
                   'disk' : 'DiskCollector'}

class Collector:
    def __init__(self, *args, **kwargs):
        self.map = {}
        self.args = args
        self.kwargs = kwargs

class CPUCollector(Collector):
    '''Uses vmstat to report CPU information'''

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def collect(self):
        '''reads the various states of the cpu and returns them'''
    
        import popen2
        stdout, stdin = popen2.popen4('vmstat')
        stdout.readline()
        stdout.readline()
        line = stdout.readline()
        vals = line.split()[-6:]
        
        self.map['deviceInterruptsPerSec'] = vals[0]
        self.map['systemCallsPerSec'] = vals[1]
        self.map['contextSwitchesPerSec'] = vals[2]
        self.map['user'] = vals[3]
        self.map['system'] = vals[4]
        self.map['idle'] = vals[5]


class MemoryCollector(Collector):
    '''Uses vmstat to read memory information.'''

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def call(self, command):
        '''calls the command provided and returns the result.  makes the
        assumption that the command is a vmstat and assumes that there
        will be 2 lines of output that will be dropped before the
        actual stats are returned.'''

        import popen2
        stdout, stdin = popen2.popen4(command)
        stdout.readline()
        stdout.readline()
        return stdout.readline()

    def collect(self):
        '''reads the memory information from both vmstat -a and /proc/meminfo
        and returns the values in a map'''
    
        # all page values are in 1024 bytes
        multiplier = 1024

        # set the page size
        import resource
        self.map['pageSize'] = resource.getpagesize()
        
        # read the vmstat values
        vals = self.call('vmstat').split()[3:]
        self.map['activeVirtual'] = int(vals[0]) * multiplier
        self.map['freeList'] = int(vals[1]) * multiplier
        self.map['pageFaultTotalCount'] = vals[2]
        self.map['pageFaultReclaimsCount'] = vals[3]
        self.map['pageFaultInCount'] = vals[4]
        self.map['pageFaultOutCount'] = vals[5]
        self.map['pageFaultFreeCount'] = vals[6]
        self.map['pageFaultScansCount'] = vals[7]


class DiskCollector(Collector):
    '''Uses df -k to read disk information.'''

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def collect(self):
        '''reads the disk information for the mount provided'''
        if len(self.args) == 0:
            raise 'No mount point defined'
        
        mount = self.args[0]

        import popen2
        stdout, stdin = popen2.popen4("df -k %s" % mount)
        lines = stdout.readlines()
        
        # mount was not located
        if len(lines) == 1:
            raise "Disk %s not found" % mount

        # extract the used and available blocks
        line = lines[-1]
        total, used, avail = line.split()[1:4]
        self.map['usedBlocks'] = used
        self.map['availBlocks'] = avail
        self.map['totalBlocks'] = total

