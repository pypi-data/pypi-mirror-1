#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
FS RDF storage
==============

Conventions used:

Objects are stored as pairtree based on id, eg.

id = "01020304"  and base dir = "storage"

gives

physical directory for id = "storage/01/02/03/04/05"

FS convention:

{id_path}/_ROOT/_XXXX => Object RDF for this ID
{id_path}/_MANIFEST/_XXXX => Manifest RDF for this ID
{id_path}/_1/_XXXX => Object RDF for this ID, subpart 1
{id_path}/_2/_XXXX => Object RDF for this ID, subpart 2
{id_path}/_3/_XXXX => Object RDF for this ID, subpart 3

XXXX is just an autoincrementing number - largest is the latest.
"""
        
import os, sys

import codecs

from rdfobject import RDFobject

from storage_exceptions import ObjectNotFoundException, ObjectAlreadyExistsException

from rdfobject.constructs import Manifest, ItemAlreadyExistsException, ItemDoesntExistException

from rdflib import Namespace


from datetime import datetime

import random

URI_BASE = "info:local/"
STORAGE_DIR = "./rdffilestore"
SPECIAL_FILE_PREFIX = "."

class FileStorageFactory(object):
    def get_store(self, uri_base=URI_BASE, store_dir=STORAGE_DIR, prefix=SPECIAL_FILE_PREFIX):
        return FileStorageClient(uri_base, store_dir, prefix)

class FileStorageObject(object):
    def __init__(self, id, fs_store_client):
        self.fs = fs_store_client
        self.id = id
        self.uri = self.fs.uri_base[id]
        self.root_uri = self.fs.uri_base["%s/%s" % (id, u"ROOT")]
        self.manifest_uri = self.fs.uri_base["%s/%s" % (id, u"MANIFEST")]
        
        #self.parts = self.fs.listParts(self.id)
        
    def putRoot(self, rdf):
        """Store the root for this object - rdf can either be
        an RDFXML string or an RDFobject"""
        if isinstance(rdf, RDFobject):
            self.fs._store_rdfobject(self.id, u'ROOT', rdf)
        else:
            r = RDFobject(self.id).from_string(rdf)
            self.fs._store_rdfobject(self.id, u'ROOT', rdf)
        
    def getRoot(self):
        """RDFObject for this object"""
        return self.fs._get_rdfobject(self.id, u'ROOT')
        
    def add_part(self, partid, bytestream):
        return self.fs._put_part(self.id, partid, bytestream)
    
    def get_part(self, partid):
        return self.fs._get_part(self.id, partid)
        
    def del_part(self, partid):
        return self.fs._del_part(self.id, partid)
    
    def listParts(self):
        pass
        
    def putManifest(self, rdf):
        """Store the manifest for this object - rdf can either be
        an RDFXML string or a Manifest"""
        if isinstance(rdf, Manifest):
            self.fs._store_manifest(self.id, u'MANIFEST', rdf)
        else:
            r = Manifest().from_string(rdf)
            self.fs._store_manifest(self.id, u'MANIFEST', rdf)
            
    def getManifest(self):
        """Manifest for this object"""
        return self.fs._get_manifest(self.id, u'MANIFEST', self.manifest_uri)
        
        
class FileStorageClient(object):
    def __init__(self, uri_base, store_dir, prefix):
        self.store_dir = store_dir
        self.uri_base = Namespace(uri_base)
        self.ids = {}
        self.id_parts = {}
        self.prefix = prefix
        self._init_store()
        
    def _get_id_from_dirpath(self, dirpath):
        path = self._get_path_from_dirpath(dirpath)
        return "".join(path)
    
    def _get_path_from_dirpath(self, dirpath):
        head, tail = os.path.split(dirpath)
        path = [tail]
        if os.name == 'posix':
            while not os.path.samefile(self.store_dir, head):
                head, tail = os.path.split(head)
                path.append(tail)
        else:
            # Ugh... damn windows
            while not self.store_dir == head:
                head, tail = os.path.split(head)
                path.append(tail)
        path.reverse()
        return path
    
    def _id_to_dirpath(self, id):
        dirpath = self.store_dir
        while id:
            dirpath = os.path.join(dirpath, id[:2])
            id = id[2:]
        return dirpath
    
    def _init_store(self):
        if not os.path.exists(self.store_dir):
            os.mkdir(self.store_dir)
            f = open(os.path.join(self.store_dir, "pairtree_version0_1"), "w")
            f.write("This directory conforms to Pairtree Version 0.1. Updated spec: http://www.cdlib.org/inside/diglib/pairtree/pairtreespec.html")
            f.close()
            f = open(os.path.join(self.store_dir, "pairtree_prefix"),"w")
            f.write(self.uri_base)
            f.close()
        elif os.path.exists(os.path.join(self.store_dir, "pairtree_prefix")):
            """Read the uri base of this store"""
            f = open(os.path.join(self.store_dir, "pairtree_prefix"),"r")
            prefix = f.read().strip()
            f.close()
            self.uri_base = Namespace(prefix)
            
        if not os.path.isdir(self.store_dir):
            raise Exception
        # load existing objects from the peartree
        for dirpath, dirnames, filenames in os.walk(self.store_dir):
            if "MANIFEST" in filenames:
                this_id = self._get_id_from_dirpath(dirpath)
                self.ids[this_id] = dirpath
                self.id_parts[this_id] = dirnames
                
    def _create(self, id):
        dirpath = self._id_to_dirpath(id)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            f = open(os.path.join(dirpath, u'MANIFEST'), 'w')
            f.write(u'rdffilestore object'.encode('utf-8'))
            f.close()
            os.mkdir(os.path.join(dirpath, u'%sROOT' % self.prefix))
            os.mkdir(os.path.join(dirpath, u'%sMANIFEST' % self.prefix))
            # Setup the root object with a datestamp
            root = RDFobject()
            root.set_uri(self.uri_base[id])
            now = datetime.now()
            root.add_triple(u'dcterms:created', now)
            self._store_rdfobject(id, u'ROOT', root)
        else:
            raise ObjectAlreadyExistsException
            
        return FileStorageObject(id, self)
    
    def _get_latest_part(self, id, prefix, part_id):
        dirpath = os.path.join(self._id_to_dirpath(id), "%s%s" % (prefix, part_id))
        if prefix:
            xml_versions = [int(x[1:]) for x in os.listdir(dirpath) if x.startswith(self.prefix)]
        else:
            xml_versions = [int(x.split(self.prefix)[-1]) for x in os.listdir(dirpath)]
            
        if xml_versions:
            return max(xml_versions), os.path.join(dirpath, "%s%s" % (prefix, max(xml_versions)))
        else:
            return 0, ""
        
    def _store_rdfobject(self, id, part_id, rdfobject):
        dirpath = os.path.join(self._id_to_dirpath(id), "%s%s" % (self.prefix, part_id))
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        current_version, current_path = self._get_latest_part(id, self.prefix, part_id)
        version_no = current_version + 1
        f = codecs.open(os.path.join(dirpath, "%s%s" % (self.prefix, version_no)), encoding='utf-8', mode='w')
        print "Writing to: %s" % (os.path.join(dirpath, "%s%s" % (self.prefix, version_no)))
        f.write(rdfobject.to_string())
        f.close()
        return version_no

    def _put_part(self, id, part_id, bytestream):
        dirpath = os.path.join(self._id_to_dirpath(id), "%s" % (part_id))
        if not os.path.exists(dirpath):        
            os.mkdir(dirpath)
        current_version, current_path = self._get_latest_part(id, "", part_id)
        version_no = current_version + 1
        f = open(os.path.join(dirpath, "%s%s%s" % (part_id, self.prefix, version_no)), "wb")
        f.write(bytestream)
        f.close()
        return version_no

    def _get_part(self, id, part_id):
        dirpath = os.path.join(self._id_to_dirpath(id), "%s" % (part_id))
        if not os.path.exists(dirpath):
            raise ObjectNotFoundException
        current_version, current_path = self._get_latest_part(id, "", part_id)
        fn = os.path.join(dirpath, "%s%s%s" % (part_id, self.prefix, current_version))
        if not os.path.exists(fn):
            raise ObjectNotFoundException
        f = open(fn, "rb")
        bytestream = f.read()
        f.close()
        return bytestream

    def _store_manifest(self, id, part_id, manifest):
        current_version, current_path = self._get_latest_part(id, self.prefix, part_id)
        next_xml = current_version + 1
        dirpath = os.path.join(self._id_to_dirpath(id), "%s%s" % (self.prefix, part_id))
        f = codecs.open(os.path.join(dirpath, "%s%s" % (self.prefix, next_xml)), encoding='utf-8', mode='w')
        f.write(manifest.to_string())
        f.close()
        return next_xml
    
    def _get_rdfobject(self, id, part_id):
        current_version, current_path = self._get_latest_part(id, self.prefix, part_id)
        r = RDFobject()
        r.set_uri(self.uri_base[id])
        if current_version > 0:
            f = codecs.open(current_path, encoding='utf-8', mode='r')
            r.from_string(self.uri_base[id], f.read())
            f.close()
        return r

    def _get_manifest(self, id, part_id, file_uri):
        current_version, current_path = self._get_latest_part(id, self.prefix, part_id)
        m = Manifest(file_uri)
        if current_version > 0:
            f = codecs.open(current_path, encoding='utf-8', mode='r')
            m.from_string(f.read())
            f.close()
        return m
    
    
    def exists(self, id):
        dirpath = os.path.join(self._id_to_dirpath(id), u'MANIFEST')
        return os.path.exists(dirpath)
    
    def _get_new_id(self):
        id = "%.14d" % random.randint(0,99999999999999)
        while self.exists(id):
            id = "%.14d" % random.randint(0,99999999999999)
        return id
    
    def getObject(self, id=None, create_if_doesnt_exist=True):
        if not id:
            id = self._get_new_id()
            return self._create(id)
        elif self.exists(id):
            return FileStorageObject(id, self)
        elif create_if_doesnt_exist:
            return self._create(id)
        else:
            raise ObjectNotFoundException
            
    def createObject(self, id):
        if self.exists(id):
            raise ObjectAlreadyExistsException
        else:
            return self._create(id)

