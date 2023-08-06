repoze.depinj
=============

A package which provides a dependency injection helper API for use in
unit test suites.

Using :mod:`repoze.depinj`
--------------------------

To use :mod:`repoze.depinj`, create unit test suites which have the
following ``setUp`` and ``tearDown``:

.. code-block:: python
   :linenos:

   import unittest

   class MyTest(unittest.TestCase):
       def setUp(self):
           from repoze.depinj import clear
           clear()

       tearDown = setUp

Then within unit tests, you can use the :mod:`repoze.depinj` API to
introduce dependency injections in your code.

The API consists of two functions that are meant to be placed into the
code which is under test: ``lookup`` and ``construct``.  It also has
two functions that are meant to be placed into the test code itself:
``inject`` and ``inject_factory``.

``lookup`` and ``inject``
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``lookup`` function returns either a domain object (a "real"
object, used in code under test) or a stub registered by a test that
uses ``inject``.  It accepts one mandatory argument: ``real``, which
should be a reference to the "real" object (the object that should be
returned when the system is not under test). 

The ``inject`` function injects an implementation that can be found
via ``lookup`` when the code is under test.  It accepts two positional
arguments ``fixture`` and ``real``.  ``fixture`` is a reference to an
object that should replace the "real" object when the system is under
test.  ``real`` is a reference to the object which will be used when
the system is not under test.  The result of ``inject_factory`` can be
ignored.

These functions are meant to be used together.

.. code-block:: python
   :linenos:

   from repoze.depinj import lookup

   class Real(object):
       """ The real implementation """
       def say_hello(self):
           return 'Hello'

   real = Real()

   def unit_under_test():
       impl = lookup(real)
       impl.say_hello()

A unit test which replaced the "real" implementation with a stub is as
follows:

.. code-block:: python
   :linenos:

   import unittest
   from repoze import depinj

   class Test_unit_under_test(unittest.TestCase):
       def setUp(self):
           from repoze.depinj import clear
           clear()

       tearDown = setUp

       def test_it(self):
           from mymodule import real
           from mymodule import unit_under_test
           class Fixture(object):
               def __init__(self, positional, keyword=None):
                   self.positional = positional
               def say_hello(self):
                   return 'Fixture hello!'
           fixture = Fixture()
           depinj.inject(fixture, real)
           result = unit_under_test()
           self.assertEqual(result, 'Fixture hello!')

``construct`` and ``inject_factory``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``construct`` function returns either the result of a domain
object which is a factory (the "real" constructor result, used when
code is not under test) or the result of a stub factory registered by
a test (used when the code is under test).   It accepts one mandatory
argument: ``real``, which should be a reference to the factory that
should do construction.  It also accepts ``*arg`` and ``**kw``.  These
values are passed to whichever constructor is found by ``construct``
(the "real" constructor or an injected constructor).

The ``inject_factory`` function injects an factory that can be found
via ``construct`` when the code is under test.  It accepts two
positional arguments ``fixture`` and ``real``.  ``fixture`` is a
reference to a factory that should replace the "real" factory when the
system is under test.  ``real`` is a reference to the factory which
will be used when the system is not under test.  ``inject_factory``
returns a "promise" callable; when the promise callable is called in a
unit test body (after the unit under test has been called), it will
return the constructed object.

These functions are meant to be used together.

.. code-block:: python
   :linenos:

   from repoze.depinj import construct

   class Real(object):
       """ The real implementation """
       def __init__(self, positional, keyword=None):
           self.positional = positional
           self.keyword = keyword

       def say_hello(self):
           return 'Hello'

   def unit_under_test():
       impl = construct(Real, 'positional', keyword=2)
       impl.say_hello()

A unit test which replaced the "real" implementation with a stub is as
follows:

.. code-block:: python
   :linenos:

   import unittest
   from repoze import depinj

   class Test_unit_under_test(unittest.TestCase):
       def setUp(self):
           from repoze.depinj import clear
           clear()

       tearDown = setUp

       def test_it(self):
           from mymodule import Real
           from mymodule import unit_under_test
           class Fixture(object):
               def __init__(self, positional, keyword=None):
                   self.positional = positional
                   self.keyword = keyword
               def say_hello(self):
                   return 'Fixture hello!'
           promise = depinj.inject_factory(Fixture, Real)
           result = unit_under_test()
           self.assertEqual(result, 'Fixture hello!')
           fixture = promise() # an instance of Fixture above
           self.assertEqual(fixture.positional, 'positional')
           self.assertEqual(fixture.keyword, 2)

``clear``
~~~~~~~~~

The ``clear`` function accepts no arguments.  It should be used to
clear the dependency injector between unit tests.

API
---

:mod:`repoze.depinj`
----------------------------------

.. automodule:: repoze.depinj

  .. autofunction:: lookup

  .. autofunction:: construct

  .. autofunction:: inject

  .. autofunction:: inject_factory

  .. autofunction:: clear

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
