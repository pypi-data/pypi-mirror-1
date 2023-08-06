===============
gocept.sequence
===============

Sequences
=========

>>> import Persistence
>>> import zope.annotation.interfaces
>>> from zope.interface import implements


We need a testobject, where the SequenceGenerator stores his data:

>>> class Dummy(Persistence.Persistent):
...     implements(zope.annotation.interfaces.IAttributeAnnotatable)

>>> test_object = zope.annotation.interfaces.IAnnotations(Dummy())


You get a SequenceGenerator by adapting to ISequenceGenerator:

>>> from gocept.sequence.interfaces import ISequenceGenerator
>>> seq_gen = ISequenceGenerator(test_object)


You get a sequence like this:

>>> seq_gen.getNextValue()
1
>>> seq_gen.getNextValue()
2
>>> seq_gen.getNextValue()
3


You can also set the generator to a value:

>>> seq_gen.setNextValue(1)
>>> seq_gen.getNextValue()
1

>>> seq_gen.setNextValue(5)
>>> seq_gen.getNextValue()
5
>>> seq_gen.getNextValue()
6
>>> seq_gen.getNextValue()
7
>>> seq_gen.getNextValue()
8


But setNextValue only accepts integer arguments:

>>> seq_gen.setNextValue('1')
Traceback (most recent call last):
...
ValueError: setNextValue expected Integer, <type 'str'> found.

>>> seq_gen.setNextValue(3.14)
Traceback (most recent call last):
...
ValueError: setNextValue expected Integer, <type 'float'> found.
