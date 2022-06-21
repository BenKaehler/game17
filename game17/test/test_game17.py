# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 05:48:53 2022

@author: Ben Kaehler
"""

__version__ = 1.1

from game17 import zombie
from game17 import game_runners
from game17 import game17 as g17

import numpy as np
from collections import Counter

test_owners = [[2, 7, 8, 4, 0, 0, 7],
               [7, 7, 6, 0, 0, 0, 0],
               [0, 6, 6, 9, 9, 9, 0],
               [7, 7, 9, 9, 9, 2, 6],
               [1, 9, 9, 9, 9, 2, 2],
               [1, 1, 9, 2, 2, 2, 1],
               [1, 7, 8, 0, 2, 2, 2]]
test_owners = np.array(test_owners)

test_numbers = [[3, 5, 1, 8, 3, 0, 22],
                [2, 0, 35, 7, 0, 3, 0],
                [0, 0, 0, 17, 0, 11, 8],
                [6, 0, 5, 0, 0, 9, 0],
                [0, 6, 0, 0, 1, 0, 11],
                [0, 16, 1, 5, 0, 0, 8],
                [1, 0, 0, 1, 1, 0, 0]]
test_numbers = np.array(test_numbers)


def test_find_owned_pieces():
    owned_pieces = g17.find_owned_pieces(2, test_owners, test_numbers)
    assert test_numbers[test_owners == 2].sum() == owned_pieces[:, 2].sum(),\
        "incorrect number of squares reported"
    for i, j, n in owned_pieces:
        assert test_owners[i, j] == 2, "reported square not owned by 2"
        assert test_numbers[i, j] == n, "incorrect number of pieces reported"


def test_make_moves_zombie():
    moves = zombie.make_moves(2, test_owners, test_numbers)
    assert isinstance(moves, list), "moves not reported in a list"
    assert isinstance(moves[0], tuple), "first element of moves not a tuple"
    assert isinstance(moves[0][0], np.ndarray), "coordinates not an array"
    pieces = Counter()
    for (i, j), direction, n in moves:
        pieces[(i, j)] += n
        assert test_owners[i, j] == 2, "moved pieces not owned"
        assert direction in "nsew", "direction not one of 'n', 's', 'e', 'w'"
    for coords, n in pieces.items():
        assert test_numbers[coords] == n, "wrong number of pieces moved"


def test_create_board():
    owners, numbers = g17.create_board(7)
    assert owners.shape == (7, 7), "board is the wrong shape"
    assert numbers.shape == (7, 7), "board is the wrong shape"
    assert (np.unique(owners) == np.arange(49)).all(), "bad owners"
    assert (numbers == 4).all(), "bad number of pieces"


def test_destination():
    in_out = [((0, 0, 'n'), (1, 0)),
              ((0, 0, 's'), (1, 0)),
              ((0, 0, 'e'), (0, 1)),
              ((0, 0, 'w'), (0, 1)),
              ((0, 1, 'n'), (1, 1)),
              ((0, 1, 's'), (1, 1)),
              ((0, 1, 'e'), (0, 0)),
              ((0, 1, 'w'), (0, 0)),
              ((1, 0, 'n'), (0, 0)),
              ((1, 0, 's'), (0, 0)),
              ((1, 0, 'e'), (1, 1)),
              ((1, 0, 'w'), (1, 1)),
              ((1, 1, 'n'), (0, 1)),
              ((1, 1, 's'), (0, 1)),
              ((1, 1, 'e'), (1, 0)),
              ((1, 1, 'w'), (1, 0))]
    for (in_i, in_j, d), (out_i, out_j) in in_out:
        test_out = g17.destination(np.array((in_i, in_j)), d, 2)
        assert isinstance(test_out, np.ndarray)
        assert (test_out == (out_i, out_j)).all(), "bad destination"


def test_update_board():
    owners = np.array(test_owners)
    numbers = np.array(test_numbers)
    moves = [(np.array([0, 0]), 's', 2),
             (np.array([0, 0]), 'w', 1),
             (np.array([3, 5]), 'n', 3),
             (np.array([3, 5]), 's', 2),
             (np.array([3, 5]), 'e', 3),
             (np.array([3, 5]), 'w', 1),
             (np.array([4, 6]), 'n', 4),
             (np.array([4, 6]), 's', 2),
             (np.array([4, 6]), 'e', 2),
             (np.array([4, 6]), 'w', 3),
             (np.array([5, 3]), 'n', 1),
             (np.array([5, 3]), 's', 1),
             (np.array([5, 3]), 'e', 1),
             (np.array([5, 3]), 'w', 2),
             (np.array([6, 4]), 's', 1)]
    g17.update_board(2, moves, owners, numbers)
    numbers_diff = numbers - test_numbers
    assert (owners[numbers_diff == 0] ==
            test_owners[numbers_diff == 0]).all(), \
        "owner changed where it shouldn't have"
    for coords, d, n in moves:
        assert owners[tuple(coords)] == 2, "owner changed after moving out"
        dest = tuple(g17.destination(coords, d, 7))
        if test_numbers[dest] > numbers_diff[dest]:
            assert owners[dest] == test_owners[dest], "bad owner change"
        elif test_numbers[dest] < numbers_diff[dest]:
            assert owners[dest] == 2, "owner not changed"
        else:
            assert owners[dest] in (2, test_owners[dest]), "bad owner change"
    for coords, d, n in moves:
        numbers_diff[tuple(coords)] += n
        dest = g17.destination(coords, d, 7)
        numbers_diff[tuple(dest)] -= n
    assert (numbers_diff == 0).all(), "numbers updated incorrectly"


def test_game17():
    n = 4
    score, times, record = game_runners.game17([], board_size=n)
    assert set(score.keys()) < set(range(n**2)), "bad players"
    assert sum(score.values()) == n**2, "bad values"
    two_zombies = {1: zombie.make_moves, 2: zombie.make_moves}
    score, times, record = game_runners.game17(two_zombies, board_size=n)
    assert set(score.keys()) < set(range(n**2)), "bad players"
    assert sum(score.values()) == n**2, "bad values"
