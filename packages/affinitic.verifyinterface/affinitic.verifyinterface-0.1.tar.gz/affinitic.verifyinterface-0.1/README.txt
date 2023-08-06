Introduction
============

What's the use to declare an interface if your class doesn't implement correctly the interface ?

Of course you should verify that in a test but if you don't want to write a test to check that all your code really implements the promised interfaces use this package.

It's a simple patch that calls ``zope.interface.verify.verifyClass`` once you declare implementing an
interface and print the BrokenImplementation or BrokenMethodImplementation as a warning (if any).
