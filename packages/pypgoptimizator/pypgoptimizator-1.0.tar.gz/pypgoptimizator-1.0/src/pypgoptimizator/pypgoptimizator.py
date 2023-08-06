#!/usr/bin/env python

import os
import optparse
import sys
import re

# script made by result of web pages reading on pgsql optimization
# http://www.varlena.com/GeneralBits/Tidbits/perf.html
def sexec(cmd):
    return os.popen(cmd).read()[:-1]

def main():
    parser = optparse.OptionParser("usage: %prog --help for usage")
    parser.add_option("-p", dest="memory",
                      default="", type="string",
                      help="Total memory in Kbytes, default to all available memory")

    parser.add_option("-i", dest="input",
                      default="", type="string",
                      help="original Postgresql.conf")
    parser.add_option("-m", dest="max_connections",
                      default="100", type="string",
                      help="max connection on the postgres")

    parser.add_option("-o", dest="output",
                      default="", type="string",
                      help="ouput Postgresql.conf")
    parser.add_option("-l", dest="log_filename",
                    default="'postgresql-%Y-%m-%d.log'", type="string",
                    help="Output logs scheme")
    parser.add_option("-b", dest="bs",
                    default="8192", type="string",
                    help="Shared buffer size")

    (options, args) = parser.parse_args()
    options.bs = int(options.bs)
    pgconf = options.input
    max_connections = int(options.max_connections)
    output = options.output
    if not os.path.exists(pgconf):
        print "Please provide a valid postgresql.conf"
        sys.exit(-1)
    
    # KERNEL OPTIMIZATION
    TotalKbytes = int(sexec("awk '/MemTotal:/ { print $2 }' /proc/meminfo"))
    # half of ree mem +cached
    if sys.platform == 'linux2':
        stmt = sexec("free 2>&1|grep Mem |awk '{print $3 \"+\" $7}'")
        exec "TotalKbytes=%s" % stmt
    
    TotalBytes = TotalKbytes * 1024
    PageSize = int(sexec('getconf PAGE_SIZE'))
    ShmallValue = TotalBytes/PageSize
    kv = {
        'kernel.shmall': ShmallValue,
        'kernel.shmmax': TotalBytes,
    }
    print "Setting KERNEL SYSCTL and recording in sysctl configuration"
    for value in kv:
        print "%s: %s" % (value, kv[value])
        print sexec('sysctl -w %s=%s' %(value, kv[value]))
        if os.path.isfile('/etc/sysctl.conf'):
            if not '%s = %s' % (value, kv[value]) in open('/etc/sysctl.conf').read():
                sexec('echo %s = %s>>/etc/sysctl.conf' % (value, kv[value]))

    # POSTGRESQL OPTIMIZATION
    print "Postgresql Configuration:"
    if options.memory:
        TotalKbytes = int(options.memory)
        TotalBytes = TotalKbytes
    # 1 buffer = 8192 bytes by default
    shared_buffers = (TotalBytes*25/100) / options.bs
    wm = (shared_buffers*10/100)
    pgvals = {
        'shared_buffers': shared_buffers,
        'effective_cache_size': shared_buffers*50/100,
        'sort_mem': wm,
        'wal_buffers': wm,
        'work_mem': shared_buffers/max_connections,

        'fsync': 'on',

        'max_connections': max_connections,
        'log_filename': options.log_filename,

        'random_page_cost': 2,
        'wal_buffers': 64,
        
        'vacuum_mem': '32MB',
        'maintenance_work_mem': '256MB',

        'logging_collector' : 'true',
        'silent_mode ': 'off',
        'log_min_duration_statement': 4,
        'log_destination':  'stderr',
    }
    if os.path.exists(pgconf):
        lines = open(pgconf).readlines()
        additional = []
        for v in pgvals:
            conf = '%s=%s\n' % (v, pgvals[v])
            found=False
            for i, l in enumerate(lines[:]):
                if re.match('^(#?)%s.*' % v, l, re.U):
                    found = True
                    lines[i] = conf
            if not found:
                additional.append(conf)
        if additional:
            lines.append('\n#\n# Added by pypgoptimizator\n#\n')
            lines.extend(additional)
        print "Patching postgresql.conf"
        open(options.output, 'w').writelines(lines)

if __name__ == '__main__':
    main()


