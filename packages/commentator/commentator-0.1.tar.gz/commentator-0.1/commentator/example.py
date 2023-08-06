import os

from middleware import Commentator
from paste.httpexceptions import HTTPExceptionHandler
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename


def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""

    keystr = 'commentator.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = StaticURLParser(app_conf['directory'])
    commentator = Commentator(app, **args)
    return HTTPExceptionHandler(commentator)
    
