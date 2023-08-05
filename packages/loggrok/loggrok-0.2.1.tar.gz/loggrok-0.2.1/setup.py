#!/usr/bin/env python

try:
    from setuptools import setup
except:
    try:
        from ez_setup import use_setuptools
        use_setuptools()
    except:
        from distutils.core import setup

setup(
    author='Drew Smathers',
    author_email='drew dot smathers at gmail dot com',
    name='loggrok',
    version='0.2.1',
    description='Simple log analysis library',
    long_description="""I wrote loggrok a while back as I needed a simple library
    for analyzing logs.  I am not actively developing loggrok, but please let me know
    if you find any bugs etc.

    Features include: 
    
    * Simple callback system (loggrok.actions) 
    * Seemless iteration over multiple rollover-index based log files - smartly joins
      broken lines (RollingIndexLogStream)
    * Custom regex-based header and message body matching.

    Example usage:

        >>> from loggrok.actions import Action
        >>> action = Action()
        >>> def printError(entry):
        ...     print 'err!', str(entry)[:-1]
        ...
        >>> action.addLevelCallback('ERROR', printError)
        >>> def printWarning(entry):
        ...     print 'warning!', str(entry)[:-1]
        ...
        >>> action.addLevelCallback('WARN', printWarning)
        >>> from loggrok.log import LogStream
        >>> stream = LogStream(fname)
        >>> stream.action = action
        >>> for entry in stream:
        ...     continue
        ...
        err! blah blah
        warning! blah blah
        err! blah blah

    You can also write your own regexes for matching custom headers:

        >>> from loggrok.parse import HeaderParser, MessageParser
        >>> header_patt = r'^([a-zA-Z]+) ([a-zA-Z]+) <(\d+)> '
        # Entry attributes correspond to groups in regex pattern
        >>> header_attrs = ('foo', 'bar', 'baz')
        >>> header_parser = HeaderParser(patt, entry_attrs)
        >>> message_patterns = (...) # regexs for message body - after header
        >>> message_attrs = (...) # tuple of attribute tuples corresponding to patters
        >>> messageParser = MessageParser(message_patterns, message_attrs)
        ...
        >>> stream.messageParser = messageParser

    See doctest in tests directory for working examples.

    To run unit tests:

        python runtests.py

    N.B. - loggrok will emit warning related to "broken" CurriedCallable class, though
    it should not cause issues.
    """,
    url='http://xix.python-hosting.com/#loggrok',
    install_requires=['xix-utils>=0.2.2'],
    packages=['loggrok'],
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Topic :: Utilities'],
    )
