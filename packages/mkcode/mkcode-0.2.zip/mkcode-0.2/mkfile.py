from mkcode import *
import os


@task
def clean():
    """ Clean out all .pyc files in sub-directories """
    for pyc in path().relpath().walkfiles('*pyc'):
        print 'Removing:', pyc
        pyc.remove()

setup = namespace('setup')

task('test', [clean, setup.test])

@task
def coverage(*a):
    """ Run nose code coverage """
    shell("nosetests --with-coverage --cover-package=mkcode", *a)

@task
def docs(*a):
    """ Generate the HTML documentation. """
    shell("rst2html.py %s README.txt > README.html" % arglist(a))

@task
def pack():
    """ Generate our distributables. """
    setup.bdist_egg()
    setup.sdist()
