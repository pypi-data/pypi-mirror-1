import zope.interface

class ISequenceGenerator(zope.interface.Interface):
    """a sequence generator returns a sequence of integers
    It's meant to be thread/ZEO safe
    New sequences start with 1
    """
    def setNextValue(next_number):
        """set the next number in the sequence"""

    def getNextValue():
        """consume and return next number in sequence"""
