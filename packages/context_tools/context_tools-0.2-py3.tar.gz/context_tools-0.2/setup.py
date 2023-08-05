try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name = 'context_tools',
    version = '0.2',
    description = "Utility functions for context managers",

    long_description = """Python 2.5's contextlib provides some handy functions for dealing with context managers, but it's pretty limited. The code in context_tools allows you to use context managers as decorators, as setUp and tearDown functions in unittest tests, and as decorators for generators.

In addition to Python 2.5 and 3.0, context_tools is available for Python 2.4.""",

    author = 'Collin Winter',
    author_email = 'collinw@gmail.com',
    url = 'http://oakwinter.com/code/context_tools',
    license = 'MIT License',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords = 'context managers decorators generators tests',
    py_modules = ['context_tools'],
)
