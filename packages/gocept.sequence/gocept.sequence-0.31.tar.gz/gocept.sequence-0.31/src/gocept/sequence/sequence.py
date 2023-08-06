# Copyright (c) 2004-2005 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: sequence.py 6166 2008-07-22 08:04:52Z sweh $
"""Adapter for generating sequences"""

import threading
import Persistence

import zope.annotation.interfaces
import zope.component
import zope.interface

import gocept.sequence.interfaces

try:
    from OFS.SimpleItem import SimpleItem as StorageBase
except ImportError:
    from Persistence import Persistent as StorageBase

class SequenceGenerator(object):
    zope.interface.implements(gocept.sequence.interfaces.ISequenceGenerator)
    zope.component.adapts(zope.annotation.interfaces.IAnnotatable)

    annotation_key = 'gocept_sequence_annotation'
    sequence_lock = threading.Lock()
    storage_lock = threading.Lock()

    def __init__(self, context):
        self.context = context

    def getNextValue(self):
        self.sequence_lock.acquire()
        try:
            # this part is required to be thread/ZEO safe
            last = self._get_last_value()
            last += 1
            self._set_last_value(last)
            return last
        finally:
            self.sequence_lock.release()

    def setNextValue(self, value):
        if not isinstance(value, (int, long)):
            raise ValueError, 'setNextValue expected Integer, %s found.' % type(value)
        self._set_last_value(value - 1)


    def _get_last_value(self):
        return self._get_sequence_storage().last_value

    def _set_last_value(self, last):
        self._get_sequence_storage().last_value = last

    def _get_sequence_storage(self):
        self.storage_lock.acquire()
        try:
            annotatable = zope.annotation.interfaces.IAnnotatable(self.context)
            seq_st = annotatable.get(self.annotation_key)
            if seq_st is None:
                # Due to a bug with plone in version 0.3 the annotation key
                # changed. Try here if the old key is in use and refactor it.
                if annotatable.get('gocept.sequence'):
                    annotatable[self.annotation_key] = annotatable['gocept.sequence']
                    del annotatable['gocept.sequence']
                    return annotatable[self.annotation_key]
                seq_st = SequenceStorage()
                annotatable[self.annotation_key] = seq_st
            return seq_st
        finally:
            self.storage_lock.release()


class SequenceStorage(StorageBase):
    """store the actual sequence value"""

    last_value = 0

    def _p_resolveConflict(self, oldState, savedState, newState):
        max_value = max(savedState['last_value'], newState['last_value'])
        savedState['last_value'] = max_value
        return savedState
