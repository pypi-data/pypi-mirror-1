#!/usr/bin/python

from simpleopt import Slot


def test_slot_empty():
    slot = Slot()
    assert slot.empty
    slot.value = 0
    assert not slot.empty

def test_slot_default():
    slot = Slot()
    assert not slot.has_default
    slot.default = 0
    assert slot.has_default

def test_slot_set_get():
    slot = Slot()
    slot.value = 10
    slot.default = 30
    slot.type = 40
    assert slot.value == 10
    assert slot.default == 30
    assert slot.type == 40

