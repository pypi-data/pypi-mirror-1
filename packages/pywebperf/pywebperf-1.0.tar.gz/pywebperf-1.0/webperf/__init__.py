'''
This tool will test the performance of your website by mimicing how a web
browser accesses it. It:

1. loads the page specified and parses the HTML as it receives it, and
2. during parsing any referenced material (images, CSS, etc) will be queued
   for retrieval by the worker threads (configurable: default is 4).

Statistics recorded include the time to first response (when we receive the
first byte of data in response to a request) and the total time for each
request.

You may also request the average time over many runs.


Usage
-----

After installation, run "pywebperf -h" to discover the usage, the most basic
of which is::

  pywebperf <url>

or, the more verbose output:

  pywebperf -v <url>


Web Interface
-------------

A simple cgi script, which may be placed in your web server's cgi-bin, is
provided. This allows simple through-the-web testing of urls, with control
over the number of repeats and threads used.
'''

__version__ = '1.0'
