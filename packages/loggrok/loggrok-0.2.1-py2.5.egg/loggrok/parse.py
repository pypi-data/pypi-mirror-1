"""Log file entry parsers
"""


from UserDict import UserDict
import sys
import re

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright 2005, Drew Smathers'
__revision__ = '$Revision: 179 $'

LOG_PATTERN_DEFAULT = re.compile(r'^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d) ([A-Z]{4,5}) *')


class LogParseException(Exception): pass

class LogParser:
    def parse(self, data):
        pass

class MessageParser(LogParser):

    def __init__(self, pattern_lookup=(), meta_keys_lookup=()):
        if pattern_lookup and meta_keys_lookup:
            repatts = []
            for patt in pattern_lookup:
                repatts.append(re.compile(patt, re.M))
            self.lookup = zip(repatts, meta_keys_lookup)
        else:
            self.lookup = None

    def parse(self, data):
        """@todo unit testing
        """
        cat = 0 # Category tells us what type of message we parsed
        if self.lookup is None:
            meta = UserDict()
            meta.category = 0
            return data, meta
        for pattern, meta_keys in self.lookup:
            match = pattern.match(data)
            if match:
                meta = UserDict()
                for index, key in enumerate(meta_keys):
                    meta[key] = match.groups()[index]
                meta.category = cat
                return match.group(), meta
            cat += 1
        raise LogParseException, 'Failed parsing message: %s' % data

class HeaderParser(LogParser):

    def __init__(self, pattern=None, meta_keys=None):
        if pattern:
            self.pattern = re.compile(pattern)
        else:
            self.pattern = LOG_PATTERN_DEFAULT
        self.meta_keys = meta_keys or ('timestamp', 'level')

    def parse(self, line):
        """@todo unit testing
        """
        match = self.pattern.match(line)
        if match is None: 
            raise LogParseException, 'Failed parsing header: %s' % line
        meta = {}
        for index, key in enumerate(self.meta_keys):
            meta[key] = match.groups()[index]
        return match.group(), meta


class ParserFactory(UserDict):
    def __call__(self, name):
        return self[name]

parserFactory = ParserFactory()
parserFactory['log.message'] = MessageParser()
parserFactory['log.header'] = HeaderParser()

