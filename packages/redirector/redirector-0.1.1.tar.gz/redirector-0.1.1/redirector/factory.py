import os
from redirector import Redirector
from paste.httpexceptions import HTTPExceptionHandler
from paste.urlparser import StaticURLParser

def factory(global_conf, **app_conf):
    """create a sample redirector"""
    assert 'app.directory' in app_conf 
    directory = app_conf['app.directory']
    assert os.path.isdir(directory)
    keystr = 'redirector.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = StaticURLParser(directory)
    redirector = Redirector(app, **args)
    return HTTPExceptionHandler(redirector)
    
