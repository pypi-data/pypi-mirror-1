#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name="cmd2",
    version="0.2.2",
    py_modules = ['cmd2','flagReader'],
    
    # metadata for upload to PyPI
    author = 'Catherine Devlin',
    author_email = 'catherine.devlin@gmail.com',
    description = "Extra features for standard library's cmd module",
    license = 'MIT',
    keywords = 'command prompt console cmd',
    url = 'http://www.assembla.com/wiki/show/python-cmd2',
    
    long_description = """Enhancements for standard library's cmd module.

Drop-in replacement adds several features for command-prompt tools:

    * Searchable command history (commands: "hi", "li", "run")
    * Load commands from file, save to file, edit commands in file
    * Multi-line commands
    * Case-insensitive commands
    * Special-character shortcut commands (beyond cmd's "@" and "!")
    * Settable environment parameters
    * Parsing commands with flags
    * Redirection to file with >, >>; input from file with <

Useable without modification anywhere cmd is used; simply import cmd2.Cmd in place of cmd.Cmd.

Usage samples at http://catherine.devlin.googlepages.com/cmd2.html
""",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    )

