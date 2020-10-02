Changelog
=========

0.7.1
-----

* Added ability to extract parts of JSON, XML and HTML responses.
  New options introduced:

  - `--extract`: Extract parts of a response content with the given expression Xpath/JSONPath expression
  - `--parser`: Set which parser to use to extract parts of a response content

* Fixed:
  - do not display chained exceptions in traceback message
  - remove trailing newlines from a cell input
* Removed Python 2.7 support
* Added notebook-based autotest: https://github.com/b3b/ipython-restmagic/blob/master/tests/notebooks/basic.ipynb
