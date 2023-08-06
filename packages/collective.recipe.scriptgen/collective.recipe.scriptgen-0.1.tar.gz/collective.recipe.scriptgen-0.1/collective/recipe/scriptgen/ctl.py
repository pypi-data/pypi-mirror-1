import subprocess
import sys


def run(args):
    cmd, cmdargs = args

    fullargs = [cmd]
    fullargs.extend(cmdargs)
    fullargs.extend(sys.argv[1:])

    return subprocess.call(fullargs)
