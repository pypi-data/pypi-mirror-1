..
    This file is part of lazr.smtptest.

    lazr.smtptest is free software: you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, version 3 of the License.

    lazr.smtptest is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
    License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with lazr.smtptest.  If not, see <http://www.gnu.org/licenses/>.

LAZR smtptest
*************

This is LAZR smtptest, a framework for testing SMTP-based applications and
libraries.  It provides a real, live SMTP server that you can send messages
to, and from which you can read those test messages.  This can be used to
ensure proper operation of your applications which send email.

.. toctree::
   :glob:

   *
   docs/*

.. _Sphinx: http://sphinx.pocoo.org/
.. _Table of contents: http://sphinx.pocoo.org/concepts.html#the-toc-tree

Importable
==========

The lazr.smtptest package is importable, and has a version number.

    >>> import lazr.smtptest
    >>> print 'VERSION:', lazr.smtptest.__version__
    VERSION: ...

More information
================

For more general usage information, see usage_.  A specific, common test
regime can be found in queue_.

.. _usage: docs/usage.html
.. _queue: docs/queue.html
