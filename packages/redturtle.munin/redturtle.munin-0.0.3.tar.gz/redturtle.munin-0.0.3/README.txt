Introduction
============

This package provides munin plugins with zope scripts which provides the data.
 * it uses `gocept.munin`_ for plugin registration. Please check it if you want towrite new plugins.
 * some plugins are based on plugins found at `munin exchange`_ (many thanks to Gaute Amundsen and Arthur Lutz)

Plugins
=======

There are 3 plugins available (new comming soon):
 * zope threads - checks free zope threads
 * zope cache parameters - checks database cache parameters
 * zodb activity - checks zodb activity

How to use it
=============

* First include it in you buildout instance slot::

    [instancne]
    ...
    eggs =
    ...
    redturtle.munin        
    
    zcml =
    ...
    redturtle.munin

* Now you should be able to call the plugins as follow::

    http://localhost:8080/@@redturtle.munin.plugins/update?munin_plugin=zopethreads

  Where `zopethreads` is you plugin name. 
  Please notice that for the security reason plugins can be called only from localhost (this will be configure better in the future)

* Now you need to make a symlink from egg to munin plugin directory::

    $ cd /opt/munin/etc/plugins
    $ ln -s ~/.buildout/eggs/redturtle.munin-0.0.3-py2.4.egg/redturtle/munin/plugins/zodb_activity.py company_zodbactivity_site1

  Where `/opt/munin/etc/plugins` is your munin directory, `~/.buildout/eggs` is you egg directory, `zodb_activity.py` the plugin you want to enable, `company` your prefix, and `site1` the name which will be shown in munin

* Finally configure the plugin in munin::

    $ cd /opt/munin/etc/plugin-conf.d/
    $ vi redturtle.conf
    ... [company_*_site1]
    ... env.AUTH myuser:myuser
    ... env.URL http://localhost:8080/@@redturtle.munin.plugins/update?munin_plugin=%s

  Where `myuser` is your zope user credential, `localhost:8080` your site url.
  Please check `munin`_ for more info about plugin configuration. 

References
==========
* `redturtle.munin`_ at pypi
* `gocept.munin`_ at pypi
* `munin`_ project
* `munin exchange`_
        
.. _redturtle.munin: http://pypi.python.org/pypi/redturtle.munin/
.. _gocept.munin: http://pypi.python.org/pypi/gocept.munin/
.. _munin exchange: http://muninexchange.projects.linpro.no/
.. _munin: http://munin.projects.linpro.no/

Author & Contact
================

.. image:: http://www.slowfoodbologna.it/redturtle_logo.png

:Author: Andrew Mleczko <``andrew.mleczko@redturtle.net``>
 
**RedTurtle Technology** 

http://www.redturtle.net
