"""
request dispatcher:
data persisting across requests should go here
"""

import os
import re

from handlers import PostComment
from model import CouchComments, PickleComments
from genshi.template import TemplateLoader
from lxml import etree
from lxmlmiddleware import LXMLMiddleware
from paste.fileapp import FileApp
from pkg_resources import resource_filename
from string import Template
from webob import Request, Response, exc

class LaxTemplate(Template):
    idpattern = r'[_a-z0-9]+'

class Commentator(LXMLMiddleware):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'database': 'commentator',
                 'template_dirs': '',
                 'pattern': '.*',
                 'path': 'html',
                 'url': '.comment',
                 'template': 'comment.html' }

    def __init__(self, app, **kw):

        self.app = app

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.auto_reload = self.auto_reload.lower() == 'true'

        # request handlers
        self.handlers = [ PostComment ]

        # template loader
        self.template_dirs = self.template_dirs.split()
        self.template_dirs.append(resource_filename(__name__, 'templates'))
        self.loader = TemplateLoader(self.template_dirs,
                                     auto_reload=self.auto_reload)

        # URL,path
        assert '#' in self.pattern
        self.url_pattern, self.xpath_pattern = self.pattern.split('#', 1)
        assert '->' in self.xpath_pattern
        self.xpath_pattern, self.mapping = [i.strip() for i in self.xpath_pattern.split('->')]

        # string template for URL substitution
        self.mapping = LaxTemplate(self.mapping)

        # backend: comment storage
        self.model = PickleComments(self.database)

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # get the path 
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.environ['path'] = path

        # save the path;  not sure why i need to do this
        environ['commentator.path_info'] = request.path_info

        # match the request to a handler
        for h in self.handlers:
            handler = h.match(self, request)
            if handler is not None:
                break
        else:
            return LXMLMiddleware.__call__(self, environ, start_response)

        # get response
        res = handler()
        return res(environ, start_response)

    def manipulate(self, environ, tree):
        url_match = re.match(self.url_pattern, environ['commentator.path_info'])
        if not url_match:
            return tree

        # make string template of the groups
        groups_dict = dict([(str(index+1), value) 
                         for index, value in enumerate(url_match.groups())])

        for element in tree.findall(self.xpath_pattern):

            # get url
            str_dict = groups_dict.copy()
            for key in element.keys():
                str_dict[key] = element.get(key)
            uri = self.mapping.substitute(str_dict)

            # get comments
            # TODO

            # genshi data
            data = {}
            data['comments'] = self.model.comments(uri)
            data['action'] = '%s/%s' % (uri, self.url)

            # render template
            template = self.loader.load(self.template)
            comments = template.generate(**data).render()
            comments = etree.fromstring(comments)
            element.append(comments)

        return tree
