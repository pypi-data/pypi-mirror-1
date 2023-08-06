import subprocess
import sys

def run(args):
    scr, defaults, packages, modules, extrapath, exitwithstatus = args

    cmdargs = [scr, 'test']
    cmdargs.extend(defaults)
    cmdargs.extend(['-s'+x for x in packages])
    cmdargs.extend(['-m'+x for x in modules])
    cmdargs.extend(['--path '+x for x in extrapath])
    if exitwithstatus:
        cmdargs.append('--exit-with-status')
    cmdargs.extend(sys.argv[1:])

    return sys.exit(subprocess.call(cmdargs))
