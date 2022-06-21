# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:18:04 2022

@author: Ben Kaehler
"""

__version__ = 1.0


import numpy as np


def find_owned_pieces(owner, owners, numbers):
    """
    Find the pieces owned by owner.

    Parameters
    ----------
    owner : int
        Owner to find the pieces for.
    owners : square array of ints
        Owners of squares.
    numbers : square array of ints
        Number of pieces in squares.

    Returns
    -------
    owned_pieces : n x 3 array of ints
        Where n is the number of non-empty squares owned by the owner.
        Each row contains the i-coordinate, the j-coordinate, and the number
        of pieces in that square.

    """
    ix = (owner == owners) & (numbers > 0)
    board_size = owners.shape[0]
    board_range = np.arange(board_size)
    from_i, from_j = np.meshgrid(board_range, board_range,
                                 indexing='ij')
    owned_pieces = np.vstack(
        (from_i[ix], from_j[ix], numbers[ix])).T
    return owned_pieces


def create_board(board_size=14):
    """
    Sets up the board. Each player initially owns one random square and
    each square initially contains four pieces.

    Parameters
    ----------
    board_size : int, optional
        The edge length of the board. The default is 14.

    Returns
    -------
    owners : square array of ints
        The owner of the square in each position.
    numbers : square array of ints
        The number of pieces in each square.

    """
    owners = np.arange(board_size**2)
    np.random.shuffle(owners)
    owners = owners.reshape((board_size, board_size))
    numbers = 4*np.ones((board_size, board_size), dtype=int)
    return owners, numbers


def destination(square, direction, board_size):
    """
    Translates a direction instruction and a starting square into the
    destination square.

    Parameters
    ----------
    square : 2-element array of ints
        The from square.
    direction : 1-character string
        'n', 's', 'e', or 'w' (for North, South, East, or West).
    board_size : int
        Edge length of the board.

    Returns
    -------
    2-element array of ints
        The destination square.

    """
    change = {'n': np.array([-1, 0]),
              's': np.array([1, 0]),
              'e': np.array([0, 1]),
              'w': np.array([0, -1])}[direction]
    return (square + change) % board_size


def update_board(owner, moves, owners, numbers):
    """
    Takes a set of moves, as generated for instance by make_moves_zombie,
    and applies them to a board.

    Parameters
    ----------
    owner : int
        Player number.
    moves : list of triples
        Each tuple contains a 2-element numpy array of ints giving the
        current coordinates of the pieces to be moved, a string giving the
        direction to move ('n', 's', 'e', or 'w'), and an int giving the
        number of pieces to move..
    owners : square array of ints
        Current owner of each square.
    numbers : square array of ints
        Current number of pieces in each square.

    Returns
    -------
    None.

    """
    board_size = owners.shape[0]
    outgoing = np.zeros_like(numbers)
    incoming = np.zeros_like(numbers)
    for square, direction, number in moves:
        to = destination(square, direction, board_size)
        if (to >= board_size).any() or (to < 0).any():
            print('player %d skipped: square coordinates out of bounds\n'
                  % owner)
            return
        if owners[tuple(square)] != owner:
            print('player %d skipped: attempt to move unowned pieces\n'
                  % owner)
            return
        outgoing[tuple(square)] += number
        incoming[tuple(to)] += number
    if (outgoing > numbers).any():
        print('player %d skipped: attempt to move more pieces than owned\n'
              % owner)
        return
    numbers -= outgoing
    ix = incoming > 0
    old_numbers = numbers[ix]
    inc_numbers = incoming[ix]
    old_owners = owners[ix]
    new_owners = owners[ix]
    for i in range(ix.sum()):
        if inc_numbers[i] < old_numbers[i]:
            new_owners[i] = old_owners[i]
        elif inc_numbers[i] > old_numbers[i]:
            new_owners[i] = owner
        else:
            new_owners[i] = np.random.choice([old_owners[i], owner])
    numbers += incoming
    owners[ix] = new_owners


def print_board(owners, numbers, print_numbers=False):
    """
    Print the state of the board. Printed as a matrix. The brightness of the
    background of each square is proportional to the number of pieces in it.
    The number in each square is the owner of that square.
    Optionally, a count of the number of pieces in each square can be
    displayed under each square.

    Parameters
    ----------
    owners : square array of ints
        Current owner of each square.
    numbers : square array of ints
        Current number of pieces in each square.
    print_numbers : bool, optional
        Whether piece counts should be explicitly shown. The default is False.

    Returns
    -------
    None.

    """
    grid = []
    n_max = numbers.max()
    for o_row, n_row in zip(owners, numbers):
        form = ''
        for o, n in zip(o_row, n_row):
            c = min(70 + n*185//n_max, 255)
            b = min(2*c, 255)
            form += ('\x1b[48;2;%d;%d;%dm' % (c, c, b)) + '%3d\x1b[0m'
        grid.append(form % tuple(o_row))
        if print_numbers:
            grid.append('%3d'*len(n_row) % tuple(n_row))
    print('\n'.join(grid))


def board_diff(before, after):
    'JSON dumpable sparse representation of a diff between 2D arrays'
    ix = after != before
    board_size = before.shape[0]
    board_range = np.arange(board_size)
    from_i, from_j = np.meshgrid(board_range, board_range,
                                 indexing='ij')
    diff = np.vstack(
        (from_i[ix], from_j[ix], after[ix])).T
    return diff


def apply_diff(before, diff):
    'Apply a diff to a 2D array'
    for i, j, after in diff:
        before[i, j] = after
