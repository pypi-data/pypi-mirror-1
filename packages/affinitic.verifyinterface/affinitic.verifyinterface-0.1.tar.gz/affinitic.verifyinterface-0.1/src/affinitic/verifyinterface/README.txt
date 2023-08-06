Simple example in testrunner:
-----------------------------

By default the egg enable interface contract verification for ``zope.interface.implements`` and
``zope.interface.classImplements`` that are present in all your packages::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     test
    ...
    ... [test]
    ... recipe = zc.recipe.testrunner
    ... eggs = affinitic.verifyinterface
    ...        zope.exceptions
    ... defaults = ['-m', 'module']
    ... """)

    >>> print system(buildout)
    Installing test.
    ...

    >>> from os.path import join
    >>> print system(join('bin', 'test')),
    <class 'affinitic.verifyinterface.tests.test_module1.Foo'> failed implementing <InterfaceClass affinitic.verifyinterface.tests.test_module1.IFoo>: An object has failed to implement interface <InterfaceClass affinitic.verifyinterface.tests.test_module1.IFoo>
    <BLANKLINE>
            The bla attribute was not provided.
    <BLANKLINE>
    <class 'affinitic.verifyinterface.tests.test_module2.Bar'> failed implementing <InterfaceClass affinitic.verifyinterface.tests.test_module2.IBar>: An object has failed to implement interface <InterfaceClass affinitic.verifyinterface.tests.test_module2.IBar>
    <BLANKLINE>
            The bla attribute was not provided.
    <BLANKLINE>
    Running zope.testing.testrunner.layer.UnitTests tests:
      Set up zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
      Ran 2 tests with 0 failures and 0 errors in 0.000 seconds.
    Tearing down left over layers:
      Tear down zope.testing.testrunner.layer.UnitTests in 0.000 seconds.


Limit verifications
-------------------

But you can limit the package where this verification needs to be done (sometimes you don't care that
a package you depend on didn't implement correctly an interface).

This is done by adding an environment variable ``verifyinterface`` where you specify what packages/modules (separated by \n as usual) you accept to verify interfaces.

Here is a simple example where I only want to have warning for bad implementation of interfaces used by module1::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     test
    ...
    ... [test]
    ... recipe = zc.recipe.testrunner
    ... eggs = affinitic.verifyinterface
    ...        zope.exceptions
    ... defaults = ['-m', 'module']
    ... environment = testenv
    ...
    ... [testenv]
    ... verifyinterface = affinitic.verifyinterface.tests.test_module1
    ... """)

    >>> print system(buildout)
    Uninstalling test.
    Installing test.
    ...

    >>> from os.path import join
    >>> print system(join('bin', 'test'))
    <class 'affinitic.verifyinterface.tests.test_module1.Foo'> failed implementing <InterfaceClass affinitic.verifyinterface.tests.test_module1.IFoo>: An object has failed to implement interface <InterfaceClass affinitic.verifyinterface.tests.test_module1.IFoo>
    <BLANKLINE>
            The bla attribute was not provided.
    <BLANKLINE>
    Running zope.testing.testrunner.layer.UnitTests tests:
      Set up zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
      Ran 2 tests with 0 failures and 0 errors in 0.000 seconds.
    Tearing down left over layers:
      Tear down zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
