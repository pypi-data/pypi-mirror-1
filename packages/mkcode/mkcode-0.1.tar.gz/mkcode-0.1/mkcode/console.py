"""
Routines for running the mk utility from a tty console and for parsing
command-line arguments.
"""

from mkcode import resolver, pathing, registry, collector
import sys
import optparse


def run_mk(*argv):
    """
    Parse the command-line arguments.  Arguments before the single
    command are for 'mk', arguments after the command are for the
    command itself (al la easy_install and setup.py).
    """
    try:
        mk_withexc(*argv)
    except OptionsError, exc:
        print usage
        print
        print '%s: %s' % (_script, exc)
        sys.exit(1)

def mk_withexc(*argv):
    """
    Same as run_mk, but exceptions are raised instead of calling sys.exit().
    """
    if not argv:
        argv = sys.argv[1:]

    opts, pargs = parse_cli(list(argv))
    mkfile = opts.get('mkfile')

    # first we need some tasks to execute
    collector.collect_all(mkfile=mkfile)

    if opts.get('list-tasks'):
        print_tasks(mkfile=mkfile)
        normal_exit()

    if not pargs:
        raise OptionsError, "You must supply at least one build target"

    target, targs = pargs[0], pargs[1:]

    if opts.get('dry-run'):
        print_resolve_order(target)
        normal_exit()

    resolver.do_command(target, targs, mkfile=mkfile)

def normal_exit():
    """ Convenience function, may be replaced with a hook. """
    sys.exit()

_script = pathing.path(sys.argv[0]).basename()
usage = """usage: %s [mkopts] [target] [targetopts]""" % _script

def parse_cli(argv):
    """
    Parse a sequence of command-line options, and return a tuple
    containing a dictionary of optional cli components, and all
    sequential args following the first non-optional component.

    For example, '-v -f mkfile foo -X' would return '-v' and '-f
    mkfile' as options, and ['foo', '-X'] as the remainder.
    """
    opts = {}
    def setopt(opt, val):
        opts[opt] = val
        
    argv.reverse()
    while argv:
        arg = argv.pop()
        if arg == '-v':
            setopt('verbose', True)
        elif arg == '-f':
            setopt('mkfile', argv.pop())
        elif arg == '-T':
            setopt('list-tasks', True)
        elif arg == '-n':
            setopt('dry-run', True)
        else:
            argv.append(arg) # put the last option back
            break
    
    argv.reverse()
    return opts, argv


def print_tasks(mkfile=None):
    """
    Print the complete task list, from all namespaces, to the console.
    """
    print "All tasks, by namespace:"
    for nsname in registry.namespaces:
        print
        print "%s:" % nsname
        ns = registry.namespace(nsname)
        for tname in ns:
            print '\t', tname
    print

    print "Default tasks:"
    for tname in registry.tasks:
        if '.' not in tname:
            print '\t', tname
    print

def print_resolve_order(goal):
    """
    Print a list of tasks that would be executed, without executing
    the task bodies, to reach the specified `goal',
    """
    for t in resolver.path_to_goal(goal):
        print t.name

class OptionsError(Exception):
    """
    Raised when there are problems with command-line options.
    """
    pass

class NormalExit(SystemExit): pass
