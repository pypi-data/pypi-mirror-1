===============
gocept.sequence
===============

Sequences
=========
>>> import Persistence
>>> import zope.annotation.interfaces
>>> import zope.interface
>>> class Dummy(Persistence.Persistent):
...     zope.interface.implements(zope.annotation.interfaces.IAttributeAnnotatable)
...
>>> test_object = zope.annotation.interfaces.IAnnotations(Dummy())
>>> from gocept.sequence.interfaces import ISequenceGenerator
>>> seq_gen = ISequenceGenerator(test_object)
>>> seq_gen.getNextValue()
1
>>> seq_gen.getNextValue()
2
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
>>> seq_gen.setNextValue('1')
Traceback (most recent call last):
...
ValueError: setNextValue expected Integer, <type 'str'> found.
