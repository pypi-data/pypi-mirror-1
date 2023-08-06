=============
munin.varnish
=============

Introduction
============

A buildout recipe that packages and configures the munin tool
*varnish_* to enable monitoring of Varnish.

Contains a copy of *varnish_* `r4144 <http://varnish.projects.linpro.no/browser/trunk/varnish-tools/munin/varnish_>`__ created by Kristian Lyngstol which
works with Varnish 2.0 or newer.


How to use it
=============

You can use it with at part like this::

    [buildout]
    parts =
      ...
      munin-varnish

    [munin-varnish]
    recipe = munin-varnish
    varnishstat = ${varnish-build:location}/bin/varnishstat

Where ``varnish-build`` would be a typical cmmi part that builds
Varnish. And the ``varnishstat`` option is the full path to the
*varnishstat* binary.

This part will create a script in the buildout bin directory called
*munin-varnish* which is used to monitor all the different aspects. The
current list of aspects available for monitoring is::

    expunge
    transfer_rates
    objects
    uptime
    request_rate
    memory_usage
    hit_rate
    threads
    backend_traffic

Each of these need to be installed as symlinks into the munin-node
plugins. For example::

    cd /etc/munin/plugins
    ln -s /path/to/buildout/bin/munin-varnish varnish_expunge


Notes
=====

* A build of *varnishstat* requires the developer's libraries for
  ncurses. If you don't have a *varnsihstat* in your build of Varnish
  then most likely you need to install the ncurses-devel or
  libncurses5-dev package and then get buildout to rebuild Varnish.

* The hit_rate aspect only works correctly with a munin server running
  version 1.4.0 alpha or better. However hit rate data is also
  available in request_rate where it is presented as raw rates rather
  than normalised as a percentage.
