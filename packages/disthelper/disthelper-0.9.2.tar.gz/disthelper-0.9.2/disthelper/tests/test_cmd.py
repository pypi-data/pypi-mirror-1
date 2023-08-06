
from fixture import TempIO
from nose.tools import eq_
from textwrap import dedent
from disthelper.cmd import *

def test_find_mod_in_setup_py_modules():
    eq_(find_mod_in_setup(dedent('''
        from distutils.core import setup        
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            py_modules=['foo'],
        )
    '''), ''), 'foo')
    
def test_find_mod_in_setup_packages():
    eq_(find_mod_in_setup(dedent('''
        from distutils.core import setup        
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            packages=[ 
                'foo', 'foo.command'],
        )
    '''), ''), 'foo')
    
def test_find_mod_in_setup_packages_ignore_multiple():
    eq_(find_mod_in_setup(dedent('''
        from distutils.core import setup
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            packages=[ 'foo', 'foo.command', 'bar', 'bar.docs'],
        )
    '''), ''), None)
    
def test_find_mod_in_setup_find_packages():
    tmp = TempIO()
    tmp.foo = 'foo'
    tmp.foo.putfile('__init__.py', '')
    
    eq_(find_mod_in_setup(dedent('''
        from setuptools import setup, find_packages
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            packages=find_packages(),
        )
    '''), tmp), 'foo')
    
def test_find_mod_in_setup_find_packages_and_exclude_list():
    tmp = TempIO()
    tmp.foo = 'foo'
    tmp.foo.putfile('__init__.py', '')
    tmp.domino = 'domino'
    tmp.domino.putfile('__init__.py', '')
    tmp.billy = 'billy'
    tmp.billy.putfile('__init__.py', '')
    
    eq_(find_mod_in_setup(dedent('''
        from setuptools import setup, find_packages
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            packages=find_packages(exclude=['domino','billy']),
        )
    '''), tmp), 'foo')
    
def test_find_mod_in_setup_find_packages_and_exclude_tuple():
    tmp = TempIO()
    tmp.foo = 'foo'
    tmp.foo.putfile('__init__.py', '')
    tmp.domino = 'domino'
    tmp.domino.putfile('__init__.py', '')
    tmp.billy = 'billy'
    tmp.billy.putfile('__init__.py', '')
    
    eq_(find_mod_in_setup(dedent('''
        from setuptools import setup, find_packages
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            packages=find_packages(exclude=('domino','billy')),
        )
    '''), tmp), 'foo')
    
def test_find_mod_in_setup_find_packages_multiple_mods():
    tmp = TempIO()
    tmp.foo = 'foo'
    tmp.foo.putfile('__init__.py', '')
    tmp.foo.distcmds = 'distcmds'
    tmp.foo.distcmds.putfile('__init__.py', '')
    
    eq_(find_mod_in_setup(dedent('''
        from setuptools import setup, find_packages
        setup(
            name = 'Foo',
            version = '0.1',
            author = 'Neal McNeal',
            author_email = 'neal@neal.com',
            description = "",
            long_description = "",
            packages=find_packages(),
        )
    '''), tmp), 'foo')
    