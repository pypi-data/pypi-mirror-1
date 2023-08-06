grokproject provides an easy way to get started with a `Grok
<http://pypi.python.org/pypi/grok>`_ web application.  Simply
install ``grokproject``::

  $ easy_install grokproject

If you have an old version of grokproject installed then you can
upgrade doing::

  $ easy_install -U grokproject

Afterwards you can run the ``grokproject`` script with the name of the
project you'd like to create as an argument::

  $ grokproject MammothHerd
  ... many lines of output here

This will not only create a project area for you to work in, it will
also download and install Grok and Zope 3 (the application server Grok
is built on).

After the project area has been created successfully, you will find an
empty Python package in the ``src`` directory in which you can place
the code for your web application.  

To start the application server, execute::

  $ cd MammothHerd
  $ bin/paster serve parts/etc/deploy.ini
  
There is also an Ajax enabled debugger 
(point your browser to http://localhost:8080/@@login.html when using this)::

  $ bin/paster serve parts/etc/debug.ini
  
Start/stop it in daemon mode::

  $ bin/mammothherd-ctl start
  $ bin/mammothherd-ctl stop
  
Start the debugger::

  $ bin/mammothherd-debug

For those who know paster: ``grokproject`` is just a wrapper around a
paster template.  So instead of running the ``grokproject`` command,
you can also run::

  $ paster create -t grok MammotHerd

To create a project with the previous ``zopectl`` layout run the ``grokproject`` 
script like::

  $ grokproject --zopectl MammothHerd

or::

  $ paster create -t grok MammothHerd zopectl=True

All configuration files used for running Grok can be found in the
``parts/etc/`` directory of your project. These configuration files
are generated automatically from the templates in ``etc/`` on each
``buildout`` run. To modify the configuration files edit the
approriate templates in ``etc/`` and rerun ``buildout`` afterwards::

  $ bin/buildout

This will rebuild the files in ``parts/etc/``.
