#!/usr/bin/python
# -*- coding: utf-8 -*-
from rdfobject import *
from rdfobject.constructs import Manifest

from datetime import datetime

class NamedGraphNotFoundException(Exception):
    pass

class Entity(object):
    def __init__(self, uri=None, manifest_uri=None):
        self._reset(uri, manifest_uri)
        self.uh = URIHelper()
    
    def _reset(self, uri, manifest_uri):
        self.parts = set([])
        self.parts_objs = {}
        self.root = RDFobject(uri)
        self.types = self.root.types
        if self.root.uri:
            self.uri = self.root.uri
        self.root.add_triple("dcterms:requires", manifest_uri)
        self.manifest = Manifest(manifest_uri)
        
    def add_namespaces(self, ns_dict):
        """Convenience method for adding namespaces"""
        for prefix in ns_dict:
            self.add_namespace(prefix, ns_dict[prefix])
        
    def add_namespace(self, prefix, ns):
        self.root.add_namespace(prefix, ns)
        self.manifest.add_namespace(prefix, ns)
        for part_uri in self.parts:
            self.parts_objs[part_uri].add_namespace(prefix, ns)
        
    def del_namespace(self, prefix):
        self.root.del_namespace(prefix)
        self.manifest.del_namespace(prefix)
        
    def add_triple(self, s,p,o, create_item=True):
        s = self.uh.parse_uri(s)
        if s == self.uri:
            self.root.add_triple(p,o)
        else:
            self.manifest.add_triple(s,p,o, create_item)

    def del_triple(self, s,p,o=None):
        s = self.uh.parse_uri(s)
        if s == self.uri:
            self.root.del_triple(p,o)
        else:
            self.manifest.del_triple(s,p,o)

    def add_type(self, uritype):
        self.root.add_type(uritype)

    def del_type(self, uritype):
        self.root.del_type(uritype)

    def to_string(self, format="xml"):
        pass
    def from_string(self, root_uri, rdfstring, format="xml"):
        pass

    def namedgraphid_to_uri(self, graph_id):
        return "%s/%s" % (self.uri, graph_id)

    def add_named_graph(self, graph_id, valid_from=datetime.now(), valid_until=None):
        uri = self.namedgraphid_to_uri(graph_id)
        if self.uh.parse_uri(uri) not in self.parts:
            r = Manifest(uri)
            
            self.parts.add(r.uri)
            self.parts_objs[r.uri] = r
            self.add_triple(r.uri, "rdf:type", "foaf:Document")
            self.add_triple(r.uri, "dc:format", "application/rdf+xml")
            self.add_triple(r.uri, 'foaf:primaryTopic', self.uri)
            self.add_triple(r.uri, "dcterms:created", datetime.now())
            if valid_from:
                self.add_triple(r.uri, "ov:validFrom", valid_from)
            if valid_until:
                self.add_triple(r.uri, "ov:validUntil", valid_until)
            return r
        else:
            return self.parts_objs[self.uh.parse_uri(uri)]

    def get_named_graph(self, graph_id, create_if_necessary=False):
        uri = self.namedgraphid_to_uri(graph_id)
        if self.uh.parse_uri(uri) not in self.parts:
            raise NamedGraphNotFoundException
        else:
            return self.parts_objs[self.uh.parse_uri(uri)]

    def del_named_graph(self, graph_id):
        uri = self.uh.parse_uri("%s/%s" % (self.uri, graph_id))
        if uri in parts:
            self.parts.remove(uri)
            del self.parts_objs[r.uri]
            self.manifest.del_item(uri)
