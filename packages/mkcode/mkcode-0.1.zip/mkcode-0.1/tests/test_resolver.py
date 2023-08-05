"""
Test the task resolution mechanisms.
"""

from mkcode import resolver, registry
from nose import with_setup
    

def clear_registry():
    registry.clear()


class FakeTask(object):
    def __init__(self, name, deps=None):
        self.name = name
        if not deps:
            deps = []
        self.dependencies = deps
        registry.tasks[name] = self


@with_setup(clear_registry)
def test_trivial_path_to_goal():
    t = FakeTask('x')
    path = resolver.path_to_goal(t)
    assert path == [t]
    
@with_setup(clear_registry)
def test_path_to_nested_tasks():
    t = FakeTask('t')
    a = FakeTask('a', [t])
    path = resolver.path_to_goal(a)
    assert path == [t, a]

@with_setup(clear_registry)
def test_exclusion_of_repeated_dependancies():
    a = FakeTask('a')
    b = FakeTask('b', [a])
    c = FakeTask('c', [b, a])
    path = resolver.path_to_goal(c)
    assert path == [a, b, c]
