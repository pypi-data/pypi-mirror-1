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

f = FileMultiEntityFactory()

print f.status

if 'fileentitytest' in f.keys():
    ora1 = f['fileentitytest'].get('info:fedora/ora:1')
    ora1.revert()
    print ora1.uri

    ora1.add_triple(ora1.uri, 'dc:name', 'Umbongo')
    print dir(ora1)
    print ora1.root.to_string()
    ora1.commit()

foo = f.add_store('foo', 'info:media/')

vid = foo.get('info:media/video:1')

vid.add_triple(vid.uri, 'dc:title', 'My Video Diary')
vid.add_triple(vid.uri, 'dc:description', 'Boring video')
vid.commit()

bar = f.clone_store('foo', 'barbar')

f.delete_store('foo')

