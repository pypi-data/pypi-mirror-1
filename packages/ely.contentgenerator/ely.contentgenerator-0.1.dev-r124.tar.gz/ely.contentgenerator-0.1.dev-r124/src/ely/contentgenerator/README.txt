Content generator for zope
--------------------------

The motivation for this is for creating test data sets in a zope
instance that can be called from python/doctests or from Zelenium
tests.

Want something that can run and algorithm if needed, such as a
recursive tree shape.

Want to be able to define some explicit shapes, e.g.::

container
    page
    page
    container
        page


Want to be able to label repeats, e.g.::

container
    page x 100
    container
        page x 10


For now will short circuit friendly syntax for an XML based one so we
can leap on lxml straight away.

Haven't used generic setup content generation because I haven't really
looked at it yet. This utility doesn't even need a profile -- woohoo.

So far there is only an implementation for Plone content - see
contentgeneration/PloneContentGenerator

testcontent1.txt provides a couple of examples. Note the 'special'
attribute values that start with 'python:' and 'file:'.

This is all very simple and convenient at the moment.
