.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Cache Alchemy, run this command in your terminal:

.. code-block:: console

    $ pipenv install cache-alchemy
    ✨🍰✨

This is the preferred method to install cache-alchemy, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for cache-alchemy can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/GuangTianLi/cache-alchemy

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/GuangTianLi/cache-alchemy/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/GuangTianLi/cache-alchemy
.. _tarball: https://github.com/GuangTianLi/cache-alchemy/tarball/master

Or using pipenv install straightly:

.. code-block:: console

    $ pipenv install -e git+https://github.com/GuangTianLi/cache-alchemy#egg=cache_alchemy
