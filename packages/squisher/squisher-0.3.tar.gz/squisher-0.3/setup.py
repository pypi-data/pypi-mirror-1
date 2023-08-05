#!/usr/bin/env python

from distutils.core import setup
import setuptools

desc = '''
Squisher can take a directory representing a Python package (i.e. a directory with __init__.py and so on) and "squish" it into a single .pyc file that you can import, or run on the command line, just like any other .py/.pyc file.

The hook is that it can be thus imported without necessarily having Squisher itself installed. All you do is run Squisher on a directory (or an existing zip file if you wish), and you get a single file you can import with any normal Python installation.

It is complementary to Eggs in a way. They're good for having packages globally installed and keeping them up-to-date, but very often you may want the simple convenience of dropping a .pyc in a directory and importing it. Furthermore, since Squished packages are just zip files with a special Python bytecode header (and Eggs are just zipfiles with internal metadata added), you can actually run it on an Egg and get a file that can be used as an Egg or a Squished package just by renaming it.
'''

setup(
    name='squisher',
    version='0.3',
    description='"squish" Python packages into importable stand-alone .pyc files',
    author='Adam Atlas',
    author_email='adam@atlas.st',
    py_modules=['squisher'],
    long_description=desc,
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
)
