collective.saoraclefixes
========================

Fix SQLAlchemy 0.4 and 0.5 Oracle quoting problems.

Monkeypatches SQLAlchemy's Oracle driver to add Oracle reserved words, and
to implement quoting of bindparameters. These fixes are a partial backport
from the 0.6 release branch.

To use, simply add an import to this package::

    import collective.saoraclefixes # apply oracle fixes

Note that the patches will only apply when SQLAlchemy versions 0.4 and 0.5 are
used. All patching activity will be logged via python's logger module with
loglevel DEBUG.

Note that the oracle reserved words list in this package is a superset of the
list in SQLAlchemy 0.6 (at least until SQLAlchemy branches/rel_0_6 r6245).
This package includes semi-reserved identifiers as defined by the `Oracle
V$RESERVED_WORDS view`_

License
-------

collective.saoraclefixes is distributed under the `MIT license
<http://www.opensource.org/licenses/mit-license.php>`_, just like SQLAlchemy.

Credits
-------

Backporting work
    `Martijn Pieters`_ at Jarn_


.. _Oracle V$RESERVED_WORDS view: http://bit.ly/nZkeD 
.. _Martijn Pieters: mailto:mj@jarn.com
.. _Jarn: http://www.jarn.com/

