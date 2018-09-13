ipython-restmagic
=================

`%%rest` : Jupyter/IPython notebook magic for HTTP queries execution.

Intended to provide similar functionality as `restclient.el <https://github.com/pashky/restclient.el>`_ - HTTP REST client tool for Emacs.


Usage
-----

.. code-block:: python

    In [1]: %load_ext restmagic

    In [2]: %%rest
       ...: POST http://httpbin.org/post
       ...: Content-Type: application/json
       ...:
       ...: {
       ...:     "some": "data",
       ...:     "array here": [
       ...:         "item 1",
       ...:         "item 2"
       ...:     ]
       ...: }


Examples
--------

See notebooks:

* `Usage example <https://github.com/b3b/ipython-restmagic/blob/master/examples/usage.ipynb>`_
* `Ethereum JSON RPC <https://github.com/b3b/ipython-restmagic/blob/master/examples/ethereum.ipynb>`_
* `Send SMS with HiLink API <https://github.com/b3b/ipython-restmagic/blob/master/examples/ethereum.ipynb>`_

Installation
------------

Latest version can be installed by executing::

    pip install git+https://github.com/b3b/ipython-restmagic

Package can be uninstalled by executing::

    pip uninstall restmagic


Related resources
-----------------

* `restclient.el <https://github.com/pashky/restclient.el>`_ : HTTP REST client tool for Emacs
* `Make Jupyter/IPython Notebook even more magical with cell magic extensions! <https://www.youtube.com/watch?v=zxkdO07L29Q>`_ : Nicolas Kruchten's talk from the PyCon Canada 2015
* `ipython-sql <https://github.com/catherinedevlin/ipython-sql>`_ : was used as an example of IPython magic
* `python-requests <https://github.com/requests/requests>`_ : used for HTTP requests
* `requests-toolbelt <https://github.com/requests/toolbelt>`_ : used for HTTP sessions information dumping
