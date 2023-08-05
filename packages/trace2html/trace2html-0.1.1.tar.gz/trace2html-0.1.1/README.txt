==========
trace2html
==========

:author: Olivier Grisel <olivier.grisel@ensta.org>

`trace2html` is a utility to convert execution coverage data obtained
with the `trace` module of the standard python library into a set of human
readable HTML documents showing sortable summary and annotated source files.

Installation
============

As usual, you can either use `sudo easy_install -U trace2html` or extract the
archive and run::

  $ sudo python setup.py install

Sample usage
============

Generate coverage data in the 'counts' file with trace.py::

  $ /usr/lib/python2.4/trace.py -mc -C coverage_dir -f counts my_testrunner.py

Write a report in directory 'coverage_dir' from data collected in 'counts'::

  $ trace2html.py -f counts -o coverage_dir
  $ firefox coverage_dir/index.html

Load data from several files (the report is written to 'coverage_dir' by
default)::

  $ trace2html.py -f file1 -f2 file2
  $ firefox coverage_dir/index.html


Licensing
=========

`trace2html` is released under the GNU/GPL v2 license (see COPYING.txt for more
details) and uses the

I would not mind relicensing `trace2html` under a more liberal license such as
the Python or ZPL licenses but that would only be useful if someone find or
write a replacement for the WebFX Sortable Table JS file under a similar
license. SortableTable.js is currently under GPLv2.

Bug reports and patches
=======================

You can directly send bug reports and patches to my personnal email address::

  olivier.grisel@ensta.org

Or you can use `bzr`__ to branch my repository::

  $ bzr branch http://champiland.homelinux.net/trace2html/code/trace2html.og.main trace2html.me.main

then publish your branch on some site and send me a merge request. Please
follow the `5-minute tutorial`__ if you are new to bzr.

Credits
=======

`trace2html` is inspired by the `cobertura project`__ for java programs. It
includes Javascript code from  WebFX Sortable Table and Cobertura.

.. References
   __`bzr`:: http://bazaar-vcs.org/
   __`5-minute tutorial`:: http://bazaar-vcs.org/QuickHackingWithBzr
   __`cobertura project`:: http://cobertura.sourceforge.net

