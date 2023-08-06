#!/usr/bin/python
# -*- coding: utf-8 -*-

from rdfobject.constructs import Entity

from rdfobject import RDFobject, NAMESPACES

from rdfobject.constructs import Manifest

from rdflib import ConjunctiveGraph

import simplejson

import logging

def _init_obj_wrapper(fn):
    def new(self, *args, **kw):
        if not self.obj:
            self.obj = self.s.getObject(self.id)
            self.uri = self.obj.uri
        return fn(self, *args, **kw)
    return new

class StoredEntity(Entity):
    def init(self, id=None, storageclient=None, **context):
        self.id = id
        self.s = storageclient
        self.obj = None
        self.context = context
        self.revert()

    @_init_obj_wrapper
    def commit(self):
        self.store_root()
        self.store_manifest()
        self.store_parts()

    @_init_obj_wrapper
    def list_parts(self):
        return self.obj.list_parts()
        
    @_init_obj_wrapper
    def list_part_versions(self, part_id):
        return self.obj.list_part_versions(part_id)
        
    @_init_obj_wrapper
    def del_part_version(self, part_id, version):
        r = self.obj.del_part_version(part_id, version)
        return r

    @_init_obj_wrapper
    def del_part_versions(self, part_id, versions, force=False):
        r = self.obj.del_part_versions(part_id, versions, force)
        return r

    @_init_obj_wrapper
    def remove_previous_versions(self, part_id):
        versions = self.obj.list_part_versions(part_id)
        versions.sort()
        most_current = versions.pop()
        self.del_part_versions(part_id, versions)
        return most_current

    @_init_obj_wrapper
    def revert(self, create_if_nonexistent=True):
        self.load_root(create_if_nonexistent)
        self.load_manifest(create_if_nonexistent)

    @_init_obj_wrapper
    def store_root(self):
        # only store the root if it has changed:
        if self.root.altered:
            self.obj.putRoot(self.root)

    @_init_obj_wrapper
    def load_root(self, create_if_nonexistent=True):
        self.root = self.obj.getRoot()

    @_init_obj_wrapper
    def put_stream(self, part_id, bytestream, commit_metadata_changes=False):
        self.obj.add_part(part_id, bytestream)
        part_uri = self.uh.parse_uri("%s/%s" % (self.uri, part_id))
        self.add_triple(self.uri, "ore:aggregates", part_uri)
        self.add_triple(part_uri, "dcterms:isPartOf", self.uri)
        if commit_metadata_changes:
            self.commit()

    @_init_obj_wrapper
    def del_stream(self, part_id, commit_metadata_changes=False):
        self.obj.del_part(part_id)
        part_uri = self.uh.parse_uri("%s/%s" % (self.uri, part_id))
        self.del_triple(self.uri, "ore:aggregates", part_uri)
        try:
            # Try to remove any triples where this part was the subject
            self.manifest.del_item(part_uri)
        except:
            pass
        if commit_metadata_changes:
            self.commit()

    @_init_obj_wrapper
    def get_stream(self, part_id, version=None):
        stream = self.obj.get_part(part_id, stream=True, version=version)
        return stream

    @_init_obj_wrapper
    def get_as_bytes(self, part_id, version=None):
        stream = self.obj.get_part(part_id, stream=False, version=version)
        return stream

    @_init_obj_wrapper
    def store_parts(self):
        for part_uri in self.parts:
            if part_uri.startswith(self.obj.uri) and self.parts_objs[part_uri].altered:
                part_id = part_uri[len(self.obj.uri)+1:]
                self.obj.add_part(part_id, self.parts_objs[part_uri].to_string())
                self.add_triple(self.uri, "ore:aggregates", part_uri)
                self.add_triple(part_uri, "dcterms:isPartOf", self.uri)

    @_init_obj_wrapper
    def store_manifest(self):
        # only store the manifest if it has changed:
        if self.manifest.altered:
            self.obj.putManifest(self.manifest)

    @_init_obj_wrapper
    def load_manifest(self, create_if_nonexistent=True):
        self.manifest = self.obj.getManifest()
        g = self.manifest.get_graph()
        if isinstance(g, ConjunctiveGraph):
            for s,p,o in g.triples(( None, NAMESPACES['foaf']['primaryTopic'], self.root.uri)):
                if s not in self.parts:
                    self.parts.add(s)
                    if s.startswith(self.obj.uri):
                        part_id = s[len(self.obj.uri)+1:]
                        r = Manifest(s)
                        r.from_string(self.obj.get_part(part_id))
                        self.parts_objs[s] = r
                    elif s.startswith("http://"):
                        r = Manifest(s)
                        r.from_url(s)
                        self.parts_objs[s] = r

    @_init_obj_wrapper
    def add_named_graph(self, graph_id, valid_from=None, valid_until=None):
        graph_uri = self.uh.parse_uri("%s/%s" % (self.uri, graph_id))
        if graph_uri not in self.parts:
            g = super(StoredEntity, self).add_named_graph(graph_id, valid_from=valid_from, valid_until=valid_until)
            self.obj.add_part(graph_id, g.to_string())
            self.commit()
            return g
        else:
            return self.parts_objs[graph_uri]

    @_init_obj_wrapper
    def del_named_graph(self, graph_id):
        super(StoredEntity, self).del_named_graph(graph_id)
        self.obj.del_part(graph_id)
        self.commit()

