=========
Demo site
=========

To look the demo follow these steps:

1) In setup.py file your project write:

   install_requires = [...'ice.adverlet',..]

2) In configure.zcml of your project write:

   <include package="ice.adverlet.demo" />

3) Run zope instance, add 'DEMO SITE' in ZMI, go to thi site, look 'DEMO'

The demo site has defined 4 adverlets: header, main, footer, sidebar.
There are default views for `header`, 'main' and `footer` adverlets
(take a look at demo/app.zcml).
Also, there are user: login - `demo`, password - `demo`.

Other way: dawnload from tarball
http://http://pypi.python.org/pypi/ice.adverlet
or http://launchpad.net/ice.adverlet/
and run buildout.
