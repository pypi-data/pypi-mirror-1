.. armsim installation file

Installation
==================================

**WARNING: armsim is still under heavy development, it is a new project and it
still has to implement a lot of the functionality needed in order to use it**

Prerequisites
-------------

* Linux
* Python 2.6
* Setuptools
* Zope Component ¿? (if you install using easy_install this isn't needed)

armsim benefits from pythons zope querying interface to find the instruction,
addressing mode, etc. that is needed in each case, that's why Zope Component
is found in the prerequisites

Using easy_install
------------------

If you have easy_install this is the easiest way of installing it:

``easy_install-2.6 armsim``

From source
------------

If you want the source code, you can get it at:

`Pypi armsim <http://pypi.python.org/pypi/armsim/>`_

run

``python2.6 setup.py install``

And you're ready to go


