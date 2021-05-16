ipython-restmagic
=================

.. start-badges
.. image:: https://img.shields.io/pypi/v/restmagic.svg
    :target: https://pypi.python.org/pypi/restmagic
    :alt: Latest version on PyPi
.. image:: https://img.shields.io/pypi/pyversions/restmagic.svg
    :target: https://pypi.python.org/pypi/restmagic
    :alt: Supported Python versions
.. image:: https://github.com/b3b/ipython-restmagic/workflows/ci/badge.svg?branch=master
     :target: https://github.com/b3b/ipython-restmagic/actions?workflow=CI
     :alt: CI Status
.. image:: https://img.shields.io/travis/b3b/ipython-restmagic.svg
    :target: https://travis-ci.org/b3b/ipython-restmagic
    :alt: Travis-CI build status
.. image:: https://codecov.io/github/b3b/ipython-restmagic/coverage.svg?branch=master
    :target: https://codecov.io/github/b3b/ipython-restmagic?branch=master
    :alt: Code coverage Status
.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/b3b/ipython-restmagic/master?filepath=examples/usage.ipynb
    :alt: Open examples in Binder
.. end-badges


`%%rest` :  IPython magic to execute HTTP requests.

:Code repository: https://github.com/b3b/ipython-restmagic
:Documentation: https://herethere.me/restmagic
:Changelog: https://github.com/b3b/ipython-restmagic/blob/master/CHANGELOG.rst



Usage
-----

.. code-block:: ipython

    In [1]: %load_ext restmagic
    In [2]: %%rest
       ...: POST https://httpbin.org/post
       ...: Content-Type: application/json
       ...: Authorization: Bearer $mytoken
       ...:
       ...: {
       ...:     "some": "data",
       ...:     "array here": [
       ...:         "item 1",
       ...:         "item 2"
       ...:     ]
       ...: }
    Out [2]: <Response [200]>


Installation
------------

Package can be installed from the PyPI by executing::

    pip install restmagic

Development version can be installed by executing::

    pip install git+https://github.com/b3b/ipython-restmagic

Package can be uninstalled by executing::

    pip uninstall restmagic


Related resources
-----------------

* `restclient.el <https://github.com/pashky/restclient.el>`__ : HTTP REST client tool for Emacs
* `Make Jupyter/IPython Notebook even more magical with cell magic extensions! <https://www.youtube.com/watch?v=zxkdO07L29Q>`__ : Nicolas Kruchten's talk from the PyCon Canada 2015
* `ipython-sql <https://github.com/catherinedevlin/ipython-sql>`__ : was used as an example of IPython magic
* `python-requests <https://github.com/requests/requests>`__ : used for HTTP requests
* `requests-toolbelt <https://github.com/requests/toolbelt>`__ : used for HTTP sessions information dumping
* `jsonpath-rw <https://github.com/kennknowles/python-jsonpath-rw>`__ : used to extract parts of JSON responses
* `lxml <https://github.com/lxml/lxml>`__ : used to extract parts of XML/HTML responses
