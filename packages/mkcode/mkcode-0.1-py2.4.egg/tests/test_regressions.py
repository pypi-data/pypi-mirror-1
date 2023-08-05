from mkcode import *
from mkcode.console import mk_withexc

trivial_mk = path('tests/trivialmkfile.py')
assert trivial_mk.exists()


def test_run_default_command():
    # The 'egg_info' command should always be available via
    # setuptools, and it should be available as a default.
    run_mk('egg_info')

def test_run_setup_command_by_namespace():
    # The 'egg_info' command should always be available via
    # setuptools.
    run_mk('setup.egg_info')

def test_run_setup_command_with_args():
    # The 'egg_info' command should always be present, and it should
    # take the '--help' argument.
    run_mk('egg_info', '--help')
    
def test_run_setup_command_with_bad_args():
    # This should blow up
    try:
        run_mk('egg_info', '--blah')
    except SystemExit:
        pass

def test_run_mkfile_from_cli():
    # we'll assume that the mkfile.py
    mk_withexc('-f', trivial_mk.abspath(), 'hello')

def test_list_all_tasks():
    try:
        mk_withexc('-f', trivial_mk.abspath(), '-T')
    except SystemExit:
        pass

def test_shell_command():
    assert shell("echo") == 0
    assert shell("echo", '1', '2', '3') == 0
