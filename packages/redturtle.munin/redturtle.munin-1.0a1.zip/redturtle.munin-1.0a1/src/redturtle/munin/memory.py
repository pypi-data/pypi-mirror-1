from os import getpid
from re import compile


def readfile(name):
    try:
        lines = open(name).readlines()
    except IOError:
        lines = ['VmSize: 0 kB']
    return lines


def vmstats(pid=getpid()):
    vm = compile(r'^(Vm[^:]*):\s*(\d+) kB$')
    for line in readfile('/proc/%s/status' % pid):
        match = vm.match(line)
        if match:
            yield match.groups()


def vmkeys():
    return [ key for key, value in vmstats() ]
