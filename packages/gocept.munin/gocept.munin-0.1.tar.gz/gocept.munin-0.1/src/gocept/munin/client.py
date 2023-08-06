#!/usr/bin/python
# -*- coding: latin-1 -*-
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Base classes and __main__ function to create munin plugins that retrieve
data in a simple format by loading URLs.

"""

import inspect
import os.path
import urllib2
import base64
import sys

class GraphBase(object):

    category = None

    def __init__(self, url, authorization, index):
        self.url = url
        self.authorization = authorization
        self.index = index

    def _prepare_fetch(self):
        url = self.url % (self.__class__.__name__)
        request = urllib2.Request(url)
        if self.authorization:
            request.add_header('Authorization', 'Basic %s' %
                               base64.encodestring(self.authorization))
        result = urllib2.urlopen(request).readlines()
        self.data = {}
        for line in result:
            key, value = line.split(':')
            self.data[key] = float(value)

    def fetch(self):
        self._prepare_fetch()
        self.do_fetch()


class SimpleGraph(GraphBase):

    title = ''
    name = ''
    key = ''

    def do_fetch(self):
        print "%s.value %s" % (self.name, self.data[self.key])

    def config(self):
        print "graph_title %s (%s)" % (self.title, self.index)
        print "graph_vlabel %s" % (self.name)
        print "graph_category %s" % self.category
        print "graph_info %s (%s) " % (self.title, self.index)
        print "%s.label %s" % (self.name, self.name)


class SimpleMultiGraph(GraphBase):

    title = ''
    vlabel = ''
    keys = []
    names = []

    def do_fetch(self):
        for key, name in zip(self.keys, self.names):
            print "%s.value %s" % (name, self.data[key])

    def config(self):
        print "graph_title %s (%s)" % (self.title, self.index)
        print "graph_vlabel %s" % (self.vlabel)
        print "graph_category %s" % self.category
        print "graph_info %s (%s) " % (self.title, self.index)
        for name in self.names:
            print "%s.label %s" % (name, name)


def main():
    """A main function for use with __main__ scripts that get linked into the
    munin plugins directory.

    Does stack inspection on the frame of the caller to find the graphs
    defined in that frame's globals.

    """
    if len(sys.argv) == 1:
        cmd = 'fetch'
    else:
        cmd = sys.argv[1]

    if cmd == '':
        cmd = 'fetch'

    script_name = os.path.basename(sys.argv[0])
    _, graph_name, index = script_name.split('_')

    url = os.environ['URL']
    authorization = os.environ.get('AUTH')

    caller = inspect.stack()[1]
    globals = caller[0].f_globals

    graph_class = globals[graph_name]
    assert issubclass(graph_class, GraphBase), "Not a graph: %s" % graph_class

    graph = graph_class(url, authorization, index)
    getattr(graph, cmd)()
