#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Adam.Dybbroe

# Author(s):

#   Adam Dybbroe <Firstname.Lastname@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""

import pytest
from unittest.mock import patch
from pyresample.spherical_utils import GetNonOverlapUnionsBaseClass
from pyresample.spherical_utils import merge_tuples
from pyresample.spherical_utils import check_keys_int_or_tuple


SET_A = {1, 3, 5, 7, 9}
SET_B = {2, 4, 6, 8, 10}
SET_C = {12, 14, 16, 18}
SET_D = set(range(10, 20))
SET_E = set(range(20, 30, 3))
SET_F = set(range(21, 30, 3))
SET_G = set(range(22, 30, 2))


def fake_merge_unions1(self, aset):
    return_value = {0: {1, 3, 5, 7, 9},
                    1: {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}}
    return return_value


def fake_merge_unions2(self, aset):
    return_value = {0: {1, 3, 5, 7, 9},
                    (2, (1, 3)): {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19},
                    (5, (4, 6)): {20, 21, 22, 23, 24, 26, 27, 28, 29}}
    return return_value


def fake_merge_tuples(intuple):
    if intuple == (2, (1, 3)):
        return (2, 1, 3)
    elif intuple == (5, (4, 6)):
        return (5, 4, 6)

    return None


@patch.object(GetNonOverlapUnionsBaseClass, '_merge_unions', fake_merge_unions1)
@patch('pyresample.spherical_utils.check_keys_int_or_tuple')
def test_merge_when_input_objects_do_not_overlap(check_keys_int_or_tuple):
    """Test main method (merge) of the GetNonOverlapUnionsBaseClass class."""

    mysets = [{1, 3, 5, 7, 9}, {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}]
    myobjects = GetNonOverlapUnionsBaseClass(mysets)

    check_keys_int_or_tuple.return_code = None

    with patch('pyresample.spherical_utils.merge_tuples', return_value=0):
        myobjects.merge()

    polygons = myobjects.get_polygons()

    assert polygons == mysets


@patch.object(GetNonOverlapUnionsBaseClass, '_merge_unions', fake_merge_unions2)
@patch('pyresample.spherical_utils.check_keys_int_or_tuple')
def test_merge_overlapping_and_nonoverlapping_objects(check_keys_int_or_tuple):
    """Test main method (merge) of the GetNonOverlapUnionsBaseClass class."""
    mysets = [SET_A, SET_B, SET_C, SET_D, SET_E, SET_F, SET_G]
    myobjects = GetNonOverlapUnionsBaseClass(mysets)

    check_keys_int_or_tuple.return_code = None

    with patch('pyresample.spherical_utils.merge_tuples') as mypatch:
        mypatch.side_effect = fake_merge_tuples
        myobjects.merge()

    polygons = myobjects.get_polygons()
    ids = myobjects.get_ids()

    expected = [{1, 3, 5, 7, 9},
                {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19},
                {20, 21, 22, 23, 24, 26, 27, 28, 29}]

    assert polygons == expected

    expected = [0, (2, 1, 3), (5, 4, 6)]

    assert ids == expected


def test_flatten_tuple():
    """Test flatten a nested tuple of integers"""

    with pytest.raises(TypeError) as exec_info:
        _ = merge_tuples(7)

    exception_raised = exec_info.value
    assert str(exception_raised) == "Function argument must be a tuple!"

    intuple = (((0, 1), (2, 3)), ((4, 5), (6, 7)))
    res = merge_tuples(intuple)

    assert res == (0, 1, 2, 3, 4, 5, 6, 7)

    intuple = (3, (1, 2))
    res = merge_tuples(intuple)

    assert res == (3, 1, 2)

    intuple = (0, (1, 2), (3, (4, 5)))
    res = merge_tuples(intuple)

    assert res == (0, 1, 2, 3, 4, 5)

    intuple = (0, (1, 2), (3, (4, 5)), (6,))
    res = merge_tuples(intuple)

    assert res == (0, 1, 2, 3, 4, 5, 6)

    intuple = (0, (1, 2), (3, (4, 5)), (6,), )
    res = merge_tuples(intuple)

    assert res == (0, 1, 2, 3, 4, 5, 6)

    intuple = (0,)
    res = merge_tuples(intuple)

    assert res == (0,)


def test_find_union_pairs():
    """Test finding a union pair."""

    listed_sets = dict(enumerate((SET_A, )))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._find_union_pair(listed_sets)

    assert retv is None

    listed_sets = dict(enumerate((SET_A, SET_B)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._find_union_pair(listed_sets)

    assert retv is None

    listed_sets = dict(enumerate((SET_C, SET_D)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._find_union_pair(listed_sets)

    assert retv == ((0, 1), set(range(10, 20)))

    listed_sets = dict(enumerate((SET_A, SET_B, SET_D)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._find_union_pair(listed_sets)

    assert retv == ((1, 2), {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19})

    listed_sets = dict(enumerate((SET_A, SET_B, SET_C, SET_D)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._find_union_pair(listed_sets)

    assert retv == ((1, 3), {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19})

    listed_sets = {0: {1, 3, 5, 7, 9},
                   4: {0, 10},
                   (2, (1, 3)): {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}}

    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._find_union_pair(listed_sets)

    assert retv == ((4, (2, (1, 3))), {0, 2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19})

    listed_sets = {0: {1, 3, 5, 7, 9},
                   (2, (1, 3)): {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}}

    this = GetNonOverlapUnionsBaseClass([])
    retv = this._find_union_pair(listed_sets)

    assert retv is None


def test_merge_unions():
    """Test merging union pairs iteratively"""

    listed_sets = dict(enumerate((SET_A, SET_B, SET_C)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._merge_unions(listed_sets)

    assert retv == {0: SET_A, 1: SET_B, 2: SET_C}

    listed_sets = dict(enumerate((SET_C, SET_D)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._merge_unions(listed_sets)

    assert retv == {(0, 1): set(range(10, 20))}

    listed_sets = dict(enumerate((SET_A, SET_B, SET_C, SET_D)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._merge_unions(listed_sets)

    assert retv == {0: {1, 3, 5, 7, 9},
                    (2, (1, 3)): {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}}

    listed_sets = {0: {1, 3, 5, 7, 9},
                   (2, (1, 3)): {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}}
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._merge_unions(listed_sets)

    assert retv == listed_sets

    listed_sets = dict(enumerate((SET_A, SET_B, SET_C, SET_D, SET_E, SET_F, SET_G)))
    this = GetNonOverlapUnionsBaseClass(listed_sets)
    retv = this._merge_unions(listed_sets)

    assert retv == {0: {1, 3, 5, 7, 9},
                    (2, (1, 3)): {2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19},
                    (5, (4, 6)): {20, 21, 22, 23, 24, 26, 27, 28, 29}}


def test_check_keys_int_or_tuple_input_okay():
    """Test the check for dictionary keys and input only a dict with the accepted keys of integers and tuples."""

    adict = {1: [1, 2, 3], (2, 3): [1, 2, 3, 4], (6, (4, 5)): [1, 2, 3, 4, 5]}
    res = check_keys_int_or_tuple(adict)
    assert res is None


def test_check_keys_int_or_tuple_input_not_okay():
    """Test the check for dictionary keys and input a dict with keys that are not an integer or a tuple."""

    adict = {1: [1, 2, 3], 'set B': [1, 2, 3, 4]}
    with pytest.raises(KeyError) as exec_info:
        _ = check_keys_int_or_tuple(adict)

    exception_raised = exec_info.value

    assert str(exception_raised) == "'Key must be integer or a tuple (of integers)'"

    adict = {1.1: [1, 2, 3]}
    with pytest.raises(KeyError) as exec_info:
        _ = check_keys_int_or_tuple(adict)

    exception_raised = exec_info.value
    assert str(exception_raised) == "'Key must be integer or a tuple (of integers)'"
