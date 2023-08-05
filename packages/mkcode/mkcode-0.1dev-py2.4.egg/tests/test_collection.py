from mkcode import collector, registry

def test_distutils_collection():
    distutils_ns = collector.collect_from_distutils()
    assert isinstance(distutils_ns, registry.Namespace)
    # 'install' will always be present, in both distutils and setuptools
    assert distutils_ns.install
    # 'test' will be present via setuptools hooks
    assert distutils_ns.test
