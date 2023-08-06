#!/usr/bin/python
# -*- coding: latin-1 -*-

from gocept.munin.client import SimpleMultiGraph, main

class zopecache(SimpleMultiGraph):
    keys = ['total_objs','total_objs_memory','target_number']
    names = ['Total_objects_in_database', 'Total_objects_in_all_caches', 'Target_number_to_cache']
    title = 'Zope cache parameters'
    category = 'Zope'

main()