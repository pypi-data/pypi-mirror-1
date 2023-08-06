Installation
------------

You must use Python 2.3+ to run webperf.

Run "python setup.py install" to install.


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


License
-------

See COPYING.txt
