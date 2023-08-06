#!/usr/bin/python
# -*- coding: latin-1 -*-

from gocept.munin.client import SimpleMultiGraph, main

class zopethreads(SimpleMultiGraph):
    keys = ['total_threads','free_threads',]
    names = ['Total_threads', 'Free threads',]
    title = 'Z2Server threads'
    category = 'Zope'

main()