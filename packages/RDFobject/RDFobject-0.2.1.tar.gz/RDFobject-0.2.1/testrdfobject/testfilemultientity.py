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

from rdfobject import FileMultiEntityFactory

from rdfobject.stores.storage_exceptions import *

from rdfobject.stores import StoreAlreadyExistsException


f = FileMultiEntityFactory()

print f.status
foo = f.add_store('foo', 'info:media/')

vid = foo.get('info:media/video:1')

vid.add_triple(vid.uri, 'dc:title', 'My Video Diary')
vid.add_triple(vid.uri, 'dc:description', 'Boring video')
vid.commit()

vid.put_stream('foobar', """Blah blah blah""")
vid.put_stream('foobar', """Blah blah blah (v2)""")

vid.put_stream('deleteme', """Blah blah blah""")
vid.put_stream('deleteme', """Blah blah blah""")
vid.put_stream('deleteme', """Blah blah blah""")
vid.commit()
# version delete

try:
    vid.del_part_version('deleteme', 1)
except VersionNotFoundException:
    print "delete me version 1 not found"

# part delete

vid.del_stream('deleteme')

print vid

print "Parts: %s" % vid.list_parts()

print "Versions of ROOT: %s" % vid.list_part_versions('ROOT')
try:
    bar = f.clone_store('foo', 'barbar')
except StoreAlreadyExistsException:
    print "Store barbar already exists."


