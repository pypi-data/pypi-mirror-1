#! /bin/env python

# tests for the Thinkwhack module

from thinkwhack import History, ThinkWhack

def test_history_limits():
    """Tests to see whether a created History instance has limits and obeys them"""
    hist = History(3)
    hist.append(1)
    hist.append(2)
    hist.append(3)
    assert hist==[1,2,3],"Assert that History with 1,2 and 3 appended is [1,2,3]"
    assert hist.get_reversed()==[3,2,1],"Assert that History.get_reversed returns the properly reversed list"
    hist.append(4)
    assert hist==[2,3,4],"Assert that the 4th value in a three value History get's popped out"
    assert hist.pop()==2,"Assert that pop returns the right element (meaning the first)"
    assert hist==[3,4], "Assert that elements are properly popped when popped"


def test_history_slicing():
    """Test whether slicing works properly"""
    hist = History(4)
    hist.append(1)
    hist.append(2)
    hist.append(3)
    hist.append(4)
    assert hist[1]==2,"Assert that hist[x] works"
    assert hist[-1]==4,"Assert that hist[-x] works"
    assert hist[1:3]==[2,3],"Assert that slices [x:x] work"

def test_history_clear():
    """Test whether history clears properly"""
    hist = History(4)
    hist.append(1)
    hist.append(2)
    hist.append(3)
    hist.append(4)
    hist.clear()
    assert hist==[],"Assert that the history is empty after clearing"
