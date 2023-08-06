Introduction
============

This package is a simple debugging tool for Zope 2 instances that are
stuck. Unlike the `z3c.deadlockdebugger`_ and `DeadlockDebugger`_ this
package also works if all threads in an instance are stuck.

If you send the *USR1* signal to a Zope2 instance with Products.signalstack
installed it will dump a stracktrace of all threads on the console.


.. _z3c.deadlockdebugger: http://pypi.python.org/z3c.deadlockdebugger
.. _DeadlockDebugger: http://www.zope.org/Members/nuxeo/Products/DeadlockDebugger

