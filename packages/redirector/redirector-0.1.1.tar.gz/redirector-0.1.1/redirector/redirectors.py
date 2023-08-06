from datetime import datetime
from dateutil.parser import parse
from ConfigParser import ConfigParser


class TestRedirector(object):
    def redirects(self):
        return [ { 'from': '/foo.txt', 'to': '/bar.txt',
                   'type': 301, 
                   'created': datetime.now(),
                   'expires': None },
                 { 'from': 'http://127.0.0.1:5521/(.*)',
                   'to': r'http://localhost:5521/\1',
                   'type': 'metarefresh',
                   'seconds': 10,
                   'created': datetime.now(),
                   'expires': None },
                 ]
    def set(self, _from, to, type=301, expires=None, seconds=None, reason=None):
        # test only....does not set anything
        return 

    def add(self, _from, to, type=301, expires=None, seconds=None):
        self.set(_from, to, type, expires, seconds)

class IniRedirector(object):
    def __init__(self, ini):
        self.ini = ini

    def redirects(self):
        parser = ConfigParser()
        parser.read(self.ini)

        redirects = []

        for section in parser.sections():
            redirect = { 'from': section }
            assert parser.has_option(section, 'to')
            assert parser.has_option(section, 'type')
            redirect['to'] = parser.get(section, 'to')
            if parser.has_option(section, 'created'):
                redirect['created'] = parse(parser.get(section, 'created'))
            else:
                redirect['created'] = None
            _type = parser.get(section, 'type')
            try:
                _type = int(_type)
            except ValueError:
                assert _type == 'metarefresh'
            redirect['type'] = _type
            if parser.has_option(section, 'expires'):
                redirect['expires'] = parse(parser.get(section, 'expires'))
            else:
                redirect['expires'] = None
            if parser.has_option(section, 'reason'):
                redirect['reason'] = parser.get(section, 'reason')
            if parser.has_option(section, 'seconds'):
                redirect['seconds'] = parser.getint(section, 'seconds')
            redirects.append(redirect)
        return redirects

    def set(self, _from, to, type=301, expires=None, seconds=None, reason=None):
        parser = ConfigParser()
        parser.read(self.ini)
        raise NotImplementedError # TODO

    def add(self, _from, to, type=301, expires=None, seconds=None):
        raise NotImplementedError # TODO
        parser = ConfigParser()
        parser.read(self.ini)
        self.set(_from, to, type, expires, seconds)
