import subprocess
import sys

def run(args):
    scr, packages, modules = args

    cmdargs = [scr, 'test']
    cmdargs.extend(['-s'+x for x in packages])
    cmdargs.extend(['-m'+x for x in modules])
    cmdargs.extend(sys.argv[1:])

    return subprocess.call(cmdargs)
