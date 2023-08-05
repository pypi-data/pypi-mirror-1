"""
Unit tests for declaring and using tasks.
"""

from mkcode.registry import lookup, task, namespace
from mkcode.resolver import NoSuchTaskError
from mkcode import registry, console, collector
from nose import with_setup


def clear_registry():
    registry.clear()

def test_clear_registry():
    registry.tasks['x'] = 1
    registry.namespaces['y'] = 1
    registry.clear()
    assert not registry.namespaces
    assert not registry.tasks

@with_setup(clear_registry)
def test_clear_registry_setup():
    assert not registry.namespaces
    assert not registry.tasks

@with_setup(clear_registry)
def test_declare_task_using_function():
    def x():
        return 'foo'
    newx = task(x)
    assert newx() == 'foo'
    assert newx.name == x.__name__
    assert newx.body is x
    assert registry.tasks.get(newx.name)() == 'foo'

@with_setup(clear_registry)
def test_declare_task_using_name():
    def x():
        return 'foo'
    newx = task('newtask')(x)
    assert newx() == 'foo'
    assert newx.name == 'newtask'
    assert newx.body is x
    newtask = registry.tasks.get('newtask')
    assert newtask() == 'foo'

@with_setup(clear_registry)
def test_task_with_namespace():
    def x():
        return 'foo'
    ns = namespace('baz')
    newx = ns.task(x)
    check_namespace_and_registries(ns, x, newx)

@with_setup(clear_registry)
def test_task_with_namespace_in_the_name():
    def x():
        return 'foo'
    newx = task('baz.x')(x)
    ns = namespace('baz')
    check_namespace_and_registries(ns, x, newx)

def check_namespace_and_registries(ns, func, ttask):
    fname = func.__name__
    assert fname in ns
    nstask = ns.get(fname)
    assert nstask
    assert nstask.body is func
    assert nstask is ttask, ttask

    # the same task should be in the tasks registry, with a full name
    qname = registry.qname(ns.name, nstask.name)
    assert qname in registry.tasks
    taskx = registry.tasks.get(qname)
    assert taskx is nstask

@with_setup(clear_registry)
def test_fetch_task_from_namespace():
    def x():
        return 'foo'
    ns = namespace('baz')
    ns.task(x)
    assert ns.x() == 'foo'

@with_setup(clear_registry)
def test_fetch_missing_task_from_namespace():
    ns = namespace('bar')
    try:
        ns.foo
    except NoSuchTaskError:
        pass
    else:
        return "oops! 'foo' should not be a member of namespace 'baz'"

@with_setup(clear_registry)
def test_print_tasks():
    collector.collect_all()
    console.print_tasks()

@with_setup(clear_registry)
def test_virtual_tasks():
    collector.collect_all()
    task('virtual:task')
    virt = lookup('virtual:task')
    assert virt
