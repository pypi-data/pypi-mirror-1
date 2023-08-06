palb - Python Apache-Like Benchmark Tool
========================================

:Author: Oliver Tonnhofer <olt@bogosoft.com>

Introduction
~~~~~~~~~~~~

``palb`` is a HTTP benchmark tool. The command line interface resembles the
Apache benchmark tool ``ab``. It lacks the advanced features of ``ab``, but it
supports multiple URLs (from arguments, files, stdin, and Python code).

``palb`` uses pycurl_ for high-performance URL retrieval and is able to handle
more than thousand requests per second with dozens of concurrent requests.
If ``pycurl`` is not available ``palb`` will fall back to Pythons ``urllib2``.

Be sure you have ``pycurl`` installed if you expect test results with more than
a few hundred requests per second. Check the output of palb::

    [...]
    Using pycurl as URL getter.
    [...]

.. _pycurl: http://pycurl.sourceforge.net/

Installation
~~~~~~~~~~~~

This package can either be installed from a .egg file using setuptools,
or from the tarball using the standard Python distutils.

If you are installing from a tarball, run the following command as an
administrative user::

    python setup.py install

If you are installing using setuptools, you don't even need to download
anything as the latest version will be downloaded for you
from the Python package index::

    easy_install --upgrade palb

If you already have the .egg file, you can use that too::

    easy_install palb-0.0.2-py2.5.egg

For best performance install ``pycurl`` (see `Introduction`_)::

    easy_install pycurl

Example & Usage
~~~~~~~~~~~~~~~

Simple usage (1 request)::

    % palb http://example.com/

Muliple requests (2 concurrent, 10 total requests)::

    % palb -c 2 -n 10 http://example.com/

Alternate between multiple URLs::

    % palb -c 2 -n 100 http://example.com/index.html\
      http://example.com/foo.html http://example.com/bar.html


Get URLs from file (use ``-`` as file name to read from stdin)::

    % cat test.txt 
    http://example.com/one.html
    http://example.com/two.html
    % palb -n 20 -f test.txt

Get URLs from python code::

    % cat test.py
    def urls(args):
        while True:
            yield 'http://example.com/'
    % palb -n 100 -u test:urls

``args`` is a list with all remaining arguments. Use it to pass options
to your own URL generators.

Here is an example output::

    % palb -c 4 -n 100 -u rndtest:random_urls 'http://localhost:5050/bar/'
    This is palb, Version 0.1.0
    Copyright (c) 2009 Oliver Tonnhofer <olt@bogosoft.com>
    Licensed under MIT License

    Using pycurl as URL getter.
    Benchmarking (be patient)..... done


    Average Document Length: 23067 bytes

    Concurrency Level:    4
    Time taken for tests: 6.469 seconds
    Complete requests:    100
    Failed requests:      0
    Total transferred:    2306704 bytes
    Requests per second:  15.46 [#/sec] (mean)
    Time per request:     250.810 [ms] (mean)
    Time per request:     62.702 [ms] (mean, across all concurrent requests)
    Transfer rate:        348.22 [Kbytes/sec] received

    Connection Times (ms)
                  min  mean[+/-sd] median   max
    Connect:       43    46   3.5     45      73
    Processing:    56   205  97.2    188     702
    Waiting:       90   100  12.6     94     138
    Total:        106   251  97.1    234     750

    Percentage of the requests served within a certain time (ms)
      50%    239
      66%    257
      75%    285
      80%    289
      90%    313
      95%    382
      98%    613
      99%    717
     100%    768 (longest request)

