"""
Routines for maintaining a registry of commands, tasks (components
that are callable from the command-line), and namespaces.
"""


tasks = {}  # our task registry
namespaces = {}  # namespaces that contain tasks


##############################
#
#  Functions for interacting with the global registries.
#


def clear():
    """ Clear the task and namespace registries """
    global tasks, namespaces
    tasks = {}
    namespaces = {}

def lookup(name, namespace=None):
    """
    Look up a task name in the registry and return the Task object for
    it.  Raises NoSuchTaskError if the task could not be found.
    """
    if namespace:
        name = qname(namespace, name)
    try:
        return tasks[name]
    except KeyError:
        raise NoSuchTaskError(name)


##############################
#
#  Routines for defining new tasks  
#


class Task(object):

    def __init__(self, name, dependencies, body):
        self.name = name
        self.dependencies = dependencies or []
        self.body = body or ( lambda: None )
        self.__doc__ = body.__doc__

    def run(self, *args, **kwds):
        return self.body(*args, **kwds)

    # TODO: does this break inheritance?
    __call__ = run


def task(name_or_f, deps=None, taskns=None):
    """
    The @task decorator.  Registers the supplied function as a
    task in the main task registry.  Registers namespaces if
    necessary.

    TODO: More docs here!
    """
    name, taskname_ns = parse_taskname(name_or_f)
    if taskname_ns:
        taskns = taskname_ns

    # we pass in None for the task body, which will default to an
    # empty callable.  This way we can throw away the new task
    # decorator and still have a functioning callable Task object.
    new_task = create_task(name, taskns, deps, None)

    def itask(func):
        new_task.body = func
        return new_task

    if callable(name_or_f):
        return itask(name_or_f)
    else:
        return itask

def create_task(name, tnamespace, deps, body):
    """ Create and register a new Task object. """
    t = Task(name, deps, body)
    if tnamespace:
        namespace(tnamespace).add_task(t)
    else:
        tasks[name] = t		# NOTE: tasks overwrite each other!
    return t


#################################
#
#  Stuff for handling namespaces
#


class Namespace(dict):

    """
    TODO: more docs here!
    """

    def __init__(self, name):
        self.__dict__['name'] = name

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise NoSuchTaskError(attr)

    def add_task(self, task):
        """
        Add a task to this namespace, and add the task to the registry
        using the fully-qualified task name.
        """
        self[task.name] = task
        fullname = self.qname(task.name)
        tasks[fullname] = task

    def task(self, taskid, *args, **kwds):
        """ Create a task in this namespace. """
        # use the @task decorator
        kwds['taskns'] = self.name
        return task(taskid, *args, **kwds)

    def qname(self, taskname):
        return qname(self.name, taskname)

def namespace(name):
    global namespaces
    ns = namespaces.setdefault(name, Namespace(name))
    return ns

def qname(nsname, taskname):
    """
    Return the fully-qualified name of a task given a task name and a
    namespace name.
    """
    return '%s.%s' % (nsname, taskname)

def split_qname(name):
    """
    Split a fully qualified task name into it's namespace and task
    name componets.  Returns a tuple of (taskname, ns).  'ns' may be
    None.

    >>> split_qname('boo') == ('boo', None)
    True
    >>> split_qname('foo.boo') == ('boo', 'foo')
    True

    """
    if '.' in name:
        ns_name, name = name.split('.', 1)
    else:
        ns_name = None
    return (name, ns_name)

def parse_taskname(name_or_f):
    """
    Return the would-be name of a task, and the task's namespace,from
    either a string or a function.

    >>> def foobar(): pass; parse_taskname(foobar) == ('foobar', None)
    True
    
    """
    if callable(name_or_f):
        name = name_or_f.__name__
    else:
        name = name_or_f
    # find and parse the namespace name and task name, if any
    return split_qname(name)


class NoSuchTaskError(Exception):
    """ Raised when the requested task doesn't exist. """

    def __init__(self, task):
        self.task = task

    def __str__(self):
        return "The task '%s' hasn't been registered" % self.task
