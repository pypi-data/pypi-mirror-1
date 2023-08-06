#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
# add rdfobject to the path, if running in the test dir
if os.path.isdir(os.path.join(os.getcwd(), 'rdfobject')):
    sys.path.append(os.getcwd())
else:
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    if os.path.isdir(os.path.join(parent_dir, 'rdfobject')):
        sys.path.append(parent_dir)
    else:
        print "Test must be run in either the test directory or the directory above it"
        quit

import rdflib

print rdflib.__version__

from rdfobject import FileEntityFactory, NAMESPACES

from rdfobject.constructs import OrganisationUnit

from datetime import datetime, timedelta

class FakeQueue(object):
    def put(self, msg):
        print "FROM THE MQ: %s" % msg

fq = FakeQueue()

f = FileEntityFactory(uri_base=u"info:fedora/", queue=fq, storage_dir="deptentitytest", prefix="_")

uri=u"info:fedora/ora:1"

dsid_root = u"info:fedora/ora:1/%s"

entity = f.get(uri)

o = OrganisationUnit(entity)

o.set_type("Institute")

o.add_namespace("lcsh", "http://id.loc.gov/authorities/")

o.add_triple(uri, "dcterms:subject", "lcsh:sh85002201#concept")
o.add_triple(uri, "dc:subject", "Aging")

p = o.get_assertion_group("first", datetime.now()-timedelta(days=2), datetime.now()-timedelta(days=1))

p.add_triple(uri, "foaf:name", "Institute of Aging")
p.add_triple(uri, "aiiso:responsibilityOf", "info:fedora/person:1")


p = o.get_assertion_group("second", datetime.now()-timedelta(days=1))

p.add_triple(uri, "foaf:name", "Institute of Âging (21st Century Institutes)")
p.add_triple(uri, "aiiso:responsibilityOf", "info:fedora/person:2")

o.commit()


o.add_namespace("lcsh", "http://id.loc.gov/authorities/")

o.add_triple(uri, "dcterms:subject", "lcsh:sh85002201#concept")
o.add_triple(uri, "dc:subject", "Aging")

o.commit()

for uri in o.list_assertion_groups():
    print "For %s" % uri
    if o.is_assertion_group_valid(uri):
        print "Is current now\n"
    else:
        print "Is NOT current now\n"
    if o.is_assertion_group_valid(uri, date=datetime.now()-timedelta(days=2)):
        print "Was current 2 days ago\n"
    else:
        print "Was NOT current 2 days ago\n"

