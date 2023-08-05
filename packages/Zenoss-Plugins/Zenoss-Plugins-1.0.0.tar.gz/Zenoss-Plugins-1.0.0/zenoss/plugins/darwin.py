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
COLLECTOR_NAMES = {'mem' : 'MemoryCollector',
                   'disk' : 'DiskCollector',
                   'process' : 'ProcessCollector'}

class Collector:
    def __init__(self, *args, **kwargs):
        self.map = {}
        self.args = args
        self.kwargs = kwargs

class MemoryCollector(Collector):
    '''Retrieves the memory information using the vm_stat command'''

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)

    def collect(self):
        '''reads the memory page information from vm_stat, and converts the
        names into camel case variables.  output from vm_stat is in pages,
        and this is then converted to bytes by extracting the page size
        from the first line of output.'''

        # read the pageSize
        import resource
        pageSize = resource.getpagesize()

        # read most of the values
        import popen2, string, re
        stdout, stdin = popen2.popen4('vm_stat')
        line = stdout.readline()
        self.map['pageSize'] = pageSize
        for line in stdout.readlines():
            # convert page labels to camelCase variables
            if line.lower().startswith('pages'):
                words, val = line.split(':')
                words = words.replace('-', ' ')
                words = words.split()

                camelWord = ''
                for word in words:
                    if string.join(words).find(word) > 0:
                        camelWord += word[0].upper() + word[1:]
                    else:
                        camelWord += word[0].lower() + word[1:]
                    
                value = int(val.replace('.', '')) * pageSize
                self.map[camelWord] = value

            # read the object cache information
            if line.lower().startswith('object cache'):
                pattern = '.*?(\\d+).*?(\\d+).*?(\\d+)%.*'
                regex = re.compile(pattern)
                match = regex.match(line)
                self.map['cacheHits'] = match.groups()[0]
                self.map['cacheLookups'] = match.groups()[1]
                self.map['cacheHitRatePercent'] = match.groups()[2]
                
    

class DiskCollector(Collector):
    '''Retrieves the disk information using the df command'''

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

class ProcessCollector(Collector):
    '''Retrieves process information via the ps command'''

    # the fields that are outputted for the process.  these come out of "man ps"
    PS_FIELDS='acflag,cpu,flags,inblk,jobc,ktrace,ktracep,lim,logname,majflt,minflt,msgrcv,msgsnd,nice,nivcsw,nsigs,nswap,nvcsw,nwchan,oublk,p_ru,paddr,pagein,pgid,ppid,pri,re,rgid,rss,rsz,ruid,ruser,sess,sig,sl,state,svuid,tdev,time,tpgid,tsess,tsiz,tt,tty,svuid,tdev,time,tpgid,tsess,tsiz,tt,tty,ucomm,uid,upr,user,vsz,wchan,xstat'

    def find(self, desc):
        '''returns the pid for the process with the desc provided.  if the
        desc is generic (e.g. httpd) then a list of pids will be returned.
        if the desc does not match any process that is found, an empty
        list is returned.'''

        import popen2
        command = 'ps -axwwo pid,command | grep %s | grep -v grep' % desc
        stdout, stdin = popen2.popen4(command)

        pids = []
        for line in stdout.readlines():
            pids.append(line.split()[0])

        return pids


    def collect(self):
        '''returns the memory and cpu information for a given process'''
        if len(self.args) == 0:
            raise 'No process defined'

        desc = self.args[0]
 
        pids = self.find(desc)

        # pick the first process in the list
        # TBD: perhaps work over all of the pids?
        import popen2
        pid = pids[0]
        command = 'ps -o "%s" -p %s' % (ProcessCollector.PS_FIELDS, pid)
        stdout, stdin = popen2.popen4(command)
        line = stdout.readline()
        vars = line.split()
    
        # read the value line
        line = stdout.readline()
        vals = line.split()
    
        # parse out the variables
        pos = 0
        for var in vars:
            self.map[var] = vals[pos]
            pos = pos + 1


class CPUCollector(Collector):
    pass

    # FIXME: this needs to be completed

    # Unfortunately under OSX reading of the various CPU states does
    # not appear to be very easy.  There is no procfs mounted to read
    # information from, and the vm_stat command does not return CPU
    # state information.  After looking at the source code for
    # MenuMeters it appears as tho the way to determine CPU state
    # information under Darwin is via the call to the function
    # "host_processor_info".  This is a kernel function, and it takes
    # some complex types as arguments.  That would be where I would
    # start if I were to implement this function.

