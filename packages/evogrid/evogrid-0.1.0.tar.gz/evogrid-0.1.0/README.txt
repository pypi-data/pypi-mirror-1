==============================
Introducing the EvoGrid system
==============================

:Author: Olivier Grisel <olivier.grisel@ensta.org>
:Description: Overview of the EvoGrid software package

EvoGrid is a component-based python framework to build
`Evolutionary Computation`_-based Machine Learning algorithms sometime also
known as `Genetic Algorithms`_

The EvoGrid design is inspired by the idea of "replicators" introduced by
Richard Dawkins in his book `The Selfish Gene`_. EvoGrid's replicators can
evolve through both classical undirected darwinian evolution or through
"intelligent" lamarckian evolution or by a combination of both. In this
respect, EvoGrid can be considered a Memetic Computational framework.

.. _`Evolutionary Computation`: http://en.wikipedia.org/wiki/Evolutionary_computation
.. _`Genetic Algorithms`: http://en.wikipedia.org/wiki/Genetic_algorithm
.. _`The Selfish Gene`: http://en.wikipedia.org/wiki/The_Selfish_Gene

.. sectnum::    :depth: 2
.. contents::   :depth: 2


3 steps quick start
===================

Open a shell and do::

  $ bzr get http://champiland.homelinux.net/evogrid/code/evogrid.og.main eg
  $ cd eg
  $ sudo python setup develop

Then read the fine tutorial_ to learn and use it.

.. _tutorial: components_overview.html


Features and documentation
==========================

Current implementation provides a set of interfaces that helps organise your
code into reusable components. EvoGrid also provides you with implementations
for representation independents components that are presented in this tutorial_.

The current state of the library provides developers with the following
components:

  - selection and replacement operators (elitist, random and tournament) such as
    those presented in the tutorial_
  - base replicator_ implementations that handle constrained search domain
  - `elite archives`_ collect the best results all along the evolution process
    (weak elitism)
  - checkpointers_ (whatching pool quality, pool evolution, counters, ...)
  - evolvers_ that support nesting and thus have a native ability to simulate
    parallel evolution (cell and island models)
  - `multi objective optimization`_ (finding Pareto optimal sets)
    servers to memoize costly fitness evaluations for instance
  - dedicated components to perform `numerical optimization`_ using the numpy
    library
  - scipy.optimize integration to build numerical hybrid GA

.. _replicator: replicators.html
.. _`elite archives`: archive.html
.. _checkpointers: checkpointers.html
.. _evolvers: evolvers.html
.. _`multi objective optimization`: multiobjective.html
.. _sharing: sharing.html
.. _caching: caching.html
.. _memcached: http://www.danga.com/memcached/
.. _`numerical optimization`: numeric.html

Planned features also include:

  - GRID computing features to distribute the computation over a network
  - web interface to monitor and control a distributed run
  - integration with existing Machine Learning components such as orange and
    libsvm for instance

Please refer to the bug tracker to get the details of what's planned for the
next milestones:

  - https://launchpad.net/products/evogrid/+milestone/0.1
  - https://launchpad.net/products/evogrid/+milestone/0.2

Requirements
============

EvoGrid needs the following dependencies installed on your system. Please note
that those dependencies are automatically installed by ``easy_install``:

  - python_ >= 2.4
  - setuptools_
  - `zope.interface`_
  - `zope.component`_
  - numpy_
  - `python-memcached`_ and optionally a memcached_ server

  ..  - matplotlib_

When doing numerical optimization, you will also need to install scipy_ manually
because it is not yet (2006/09/14) installable through setuptools.

And for the developers (optional):

  - `zope.testing`_ (better doctest implementation and testrunner)
  - `trace2html`_ (html coverage reports)
  - pyflakes_ (fast linter for python)
  - exhuberant ctags

Use the included Makefile to conveniently use these tools.


Install
=======

If you want to use ``easy_install`` you should be able to do something like::

  $ sudo easy_install evogrid

Otherwise you can downlod the latest source archive from the cheeseshop::

  http://cheeseshop.python.org/pypi/evogrid

Then unpack and run::

  $ sudo python setup.py install

Note that you *must* have setuptools installed to get evogrid and its
dependencies automatically installed. If you don't please run::

  $ sudo python ez_setup.py


Developers
==========

The EvoGrid project is `hosted on launchpad.net`_. I use bzr_ as revision
control system. You can fork the `main branch`_ with::

  $ bzr branch http://champiland.homelinux.net/evogrid/code/evogrid.og.main \
    evogrid.my.main

If you don't know bzr_ please have a look at this `5 minutes tutorial`_.

To setup a complete ``EvoGrid`` development sandbox (with all dependencies up)::

  $ cd evogrid.my.main/
  $ sudo python setup.py develop

This will install all dependencies plus a fake ``evogrid`` egg in your
``site-packages`` that points to your developer sandbox.

You can run the tests with the following command::

  $ python setup tests

Have a look at the ``Makefile`` for more useful utilities such as how to run
``trace2html`` to generate the following the following `test coverage report`_
in order to quickly spot code areas that are under tested.

.. _`test coverage report`: coverage/index.html

Please `file bug reports`_ on the launchpad bug tracking system.


Licensing
=========

EvoGrid is available under the GNU General Public License (v2 or later). Please
refer to the COPYING.txt file for details. The documentation (in the doc/
folder is also available under the terms of the Creative Commons Attribution
license.

If you don't like those terms and would prefer a more liberal license such as
BSD/MIT/ZPL/Python license, please feel free to contact me so that I change my
mind. In the mean time it's GPL :)

.. _`python`: http://python.org
.. _`setuptools`: http://peak.telecommunity.com/DevCenter/setuptools
.. _`zope.interface`: http://download.zope.org/distribution
.. _`zope.component`: http://download.zope.org/distribution
.. _numpy: http://www.numpy.org/
.. _matplotlib: http://matplotlib.sourceforge.net/
.. _scipy: http://www.scipy.org/
.. _`python-memcached`: ftp://ftp.tummy.com/pub/python-memcached/
.. _`zope.testing`: http://download.zope.org/distribution
.. _`trace2html`: http://cheeseshop.python.org/pypi/trace2html
.. _`pyflakes`: http://divmod.org/projects/pyflakes
.. _`hosted on launchpad.net`: https://launchpad.net/products/evogrid
.. _`main branch`: https://launchpad.net/people/olivier-grisel/+branch/evogrid/og.main
.. _bzr: http://bazaar-vcs.org/
.. _`5 minutes tutorial`: http://bazaar-vcs.org/QuickHackingWithBzr
.. _`file bug reports`: https://launchpad.net/products/evogrid/+filebug

