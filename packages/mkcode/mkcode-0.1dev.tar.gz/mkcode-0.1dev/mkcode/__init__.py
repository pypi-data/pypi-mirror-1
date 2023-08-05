from console import run_mk
from registry import task, namespace
from pathing import path
import os

def shell(command, *a):
    """
    A convenient alias for calling a command with arguments via os.system().
    """
    return os.system('%s %s' % (command, arglist(a)))

def arglist(a):
    """
    Turn a number of arguments into a shell argument list: a1... aN
    """
    return ' '.join(a)

__all__ = ['path', 'task', 'namespace', 'run_mk', 'shell', 'arglist']
