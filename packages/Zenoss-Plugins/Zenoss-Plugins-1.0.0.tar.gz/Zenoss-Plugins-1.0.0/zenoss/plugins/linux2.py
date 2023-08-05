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
                   'io' : 'IOCollector',
                   'disk' : 'DiskCollector',
                   'process' : 'ProcessCollector',
                   'mem' : 'MemoryCollector'}


class Collector:
    def __init__(self, *args, **kwargs):
        self.map = {}
        self.args = args
        self.kwargs = kwargs
    
    
class CPUCollector(Collector):
    '''
    Collector that reads cpu information from /proc
    '''

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def collect(self):
        '''reads the values from the operating system'''
        
        # read values out of proc
        fp = open('/proc/stat')
        vals = fp.readline().split()
        self.map['ssCpuRawUser'] = vals[1]
        self.map['ssCpuRawNice'] = vals[2]
        self.map['ssCpuRawSystem'] = vals[3]
        self.map['ssCpuRawKernel'] = vals[3]
        self.map['ssCpuRawIdle'] = vals[4]

        # old kernels don't report these values, so try to read them
        try: 
            self.map['ssCpuRawWait'] = vals[5]
            self.map['ssCpuRawInterrupt'] = vals[6]
        except:
            pass

        # don't forget context switch information (if available)
        for line in fp.readlines():
            vals = line.split()
            name = vals[0]

            if name == 'ctxt':
                self.map['ssRawContexts'] = int(vals[1])
            if name == 'intr':
                self.map['ssRawInterrupts'] = int(vals[1])

        # pick up the load averages
        vals = open('/proc/loadavg').read().split()
        self.map['laLoadInt1'] = vals[0]
        self.map['laLoadInt5'] = vals[1]
        self.map['laLoadInt15'] = vals[2]
        
        
class IOCollector(Collector):
    '''
    Collector that reads io information from /proc
    '''

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def collect(self):
        '''reads io values out of proc'''
        for line in open('/proc/vmstat').readlines():
            name, value = line.split()
            value = int(value.replace('\n', ''))

            # for some reason net-snmp treats pgpgin as rawSent, and
            # pgpgout as rawReceived, and multiplies them by 2 (???)
            if name == 'pgpgin':
                self.map['ssIORawSent'] = value * 2
            elif name == 'pgpgout':
                self.map['ssIORawReceived'] = value * 2
            elif name == 'pswpin':
                self.map['ssRawSwapIn'] = value
            elif name == 'pswpout':
                self.map['ssRawSwapOut'] = value
        
    
class DiskCollector(Collector):
    '''
    Collector that reads disk information from /proc
    '''

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

        # only produce output if 
        if len(lines) == 1:
            raise "Disk %s not found" % mount
        
        line = lines[-1]
        total, used, avail = line.split()[1:4]
        self.map = {'usedBlocks' : used,
                    'availBlocks' : avail,
                    'totalBlocks' : total}

        
class ProcessCollector(Collector):
    '''Retrieves the CPU and memory usage for a process or a set of
    processes that match a search criteria'''

    # keys in the map
    MEMORY_LABEL = 'mem'
    CPU_LABEL = 'cpu'
    USER_LABEL = 'user'
    SYSTEM_LABEL = 'system'

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def find(self, desc):
        '''returns the pid for the process with the desc provided.  if the
        desc is generic (e.g. httpd) then a list of pids will be
        returned.  if the desc does not match any process that is
        found, an empty list is returned.'''

        import popen2, os
    
        command = 'ps axwo pid,command | grep "%s" | grep -v grep' % desc
        stdout, stdin = popen2.popen4(command)

        pids = []
        for line in stdout.readlines():
            pid = line.split()[0]
            if pid != os.getpid():
                pids.append(pid)

        return pids

    def readProcCpu(self, pid):
        '''reads cpu usage information about the process identified from
        /proc.  the cpu information is inserted into the map if the
        process has not been reported on before, or it is added to the
        total if cpu information has already been collected.  '''

        # read the values from the stat file for the process
        vals = open('/proc/%s/stat' % pid).read().split()
        user, system = vals[13:15]
        user = int(user)
        system = int(system)

        # sum both user and system to be consistent with snmp output
        cpu = user + system
    
        if not self.map.has_key(ProcessCollector.CPU_LABEL):
            # insert values into the map
            self.map[ProcessCollector.CPU_LABEL] = cpu
            self.map[ProcessCollector.USER_LABEL] = user
            self.map[ProcessCollector.SYSTEM_LABEL] = system
        else:
            # add values into existing map:
            self.map[ProcessCollector.CPU_LABEL] += cpu
            self.map[ProcessCollector.USER_LABEL] += user
            self.map[ProcessCollector.SYSTEM_LABEL] += system

    def readProcMem(self, pid):
        ''' reads memory information about the process identified from /proc.
        the memory information is inserted into the map, or if
        previous memory information is located the memory information
        requested is added to the total.'''

        import resource
        pageSize = resource.getpagesize()

        # read the values from the stat file for the process
        pages = int(open('/proc/%s/stat' % pid).read().split()[23]) + 3
        mem = pages * pageSize
    
        if not self.map.has_key(ProcessCollector.MEMORY_LABEL):
            # insert values into the map
            self.map[ProcessCollector.MEMORY_LABEL] = mem
        else:
            # add values into existing map:
            self.map[ProcessCollector.MEMORY_LABEL] += mem

    def collect(self):
        '''returns the memory and cpu information for a given process'''
        if len(self.args) == 0:
            raise 'No process defined'

        # find the PIDs for the process described
        desc = self.args[0]
        pids = self.find(desc)

        # examine all the processes in the list, summing the usage
        for pid in pids:
            cmdline = open('/proc/%s/cmdline' % pid).read()
            self.readProcCpu(pid)
            self.readProcMem(pid)


class MemoryCollector(Collector):
    ''' Retrieves the memory information, include the amount of virtual
    memory used, the amount of idle memory, the amount of memory used
    as buffers, the amount of memory used as cache, the amount of
    inactive memory, and the amount of active memory.  also returns
    the amount of memory swapped in and out of the disk.  '''

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

    def parse(self, unit):
        '''parses the unit (e.g. "kB", "MB", "B") and returns a number that
        represents the number of bytes to multiply in order to get to
        1 of said unit.  for kB the returned value is 1024, MB it is
        1024 * 1024.'''

        if unit == 'B':
            return 1
        if unit == 'kB':
            return 1024
        if unit == 'MB':
            return 1024 * 1024
    
    def collect(self):
        '''reads the memory information from both vmstat -a and /proc/meminfo
        and returns the values in a map'''

        # read values from proc
        for line in open('/proc/meminfo').readlines():
            # convert the variable to camel case
            var, value = line.split(':')

            if "MemTotal" == var:
                value, unit = value.split()
                self.map['hrMemorySize'] = int(value) * self.parse(unit)

            if "MemFree" == var:
                value, unit = value.split()
                self.map['memAvailReal'] = int(value) * self.parse(unit)

            if "SwapTotal" == var:
                value, unit = value.split()
                self.map['hrSwapSize'] = int(value) * self.parse(unit)

            if "SwapFree" == var:
                value, unit = value.split()
                self.map['memAvailSwap'] = int(value) * self.parse(unit)
                

        # read the pageSize
        import resource
        self.map['pageSize'] = resource.getpagesize()


