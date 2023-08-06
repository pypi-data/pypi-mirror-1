#!/usr/bin/python
# -*- coding: latin-1 -*-

from gocept.munin.client import SimpleMultiGraph, main

class zodbactivity(SimpleMultiGraph):
    keys = ['total_load_count','total_store_count','total_connections']
    names = ['Total_objects_loaded', 'Total_objects_stored', 'Total_connections']
    title = 'ZODB Activity'
    category = 'Zope'

main()