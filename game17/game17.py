# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:18:04 2022

@author: Ben Kaehler
"""

__version__ = 1.1

import time
from collections import defaultdict

import numpy as np
import pandas as pd

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
    owned_pieces =  np.vstack(
        (from_i[ix], from_j[ix], numbers[ix])).T
    return owned_pieces


def make_moves(owner, owners, numbers):
    """
    Takes the current state of play as input and recommends moves for the 
    pieces owned by owner. The owner can move up to the number of pieces 
    that they own in each square. The output is a list of moves. Each
    move specifies the square of origin for the pieces, the direction
    in which they should be moved, and the number of pieces. The square
    of origin is specified by its coordinates. Coordinates are numpy-array
    or zero-indexed matrix style, so (0, 0) is top left. Note that more
    than one or no moves can come from each square that the owner currently
    owns.

    Parameters
    ----------
    owner : int
        Your player number.
    owners : square array of ints
        Current owner of each square.
    numbers : square array of ints
        Current number of pieces in each square.

    Returns
    -------
    list of triples
        Each tuple contains a 2-element numpy array of ints giving the 
        current coordinates of the pieces to be moved, a string giving the 
        direction to move ('n', 's', 'e', or 'w'), and an int giving the 
        number of pieces to move.

    """
    # replace the body of this function with your code
    return make_moves_zombie(owner, owners, numbers)


def make_moves_zombie(owner, owners, numbers):
    """
    Zombie mover. Moves each owned piece in a random direction.

    Parameters
    ----------
    owner : int
        Player number.
    owners : square array of ints
        Current owner of each square.
    numbers : square array of ints
        Current number of pieces in each square.

    Returns
    -------
    list of triples
        Each tuple contains a 2-element numpy array of ints giving the 
        current coordinates of the pieces to be moved, a string giving the 
        direction to move ('n', 's', 'e', or 'w'), and an int giving the 
        number of pieces to move.

    """
    owned_pieces = find_owned_pieces(owner, owners, numbers)
    square = []
    direction = []
    number = []
    for pieces in owned_pieces:
        coords = pieces[:2]
        count = pieces[2]
        moves = np.random.multinomial(count, [0.25]*4)
        for i in range(4):
            if moves[i] > 0:
                square.append(coords)
                direction.append('nsew'[i])
                number.append(moves[i])
    return list(zip(square, direction, number))


def create_board(board_size = 14):
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
            print('square coordinates out of bounds\n')
            return
        if owners[tuple(square)] != owner:
            print('attempt to move unowned pieces\n')
            return
        outgoing[tuple(square)] += number
        incoming[tuple(to)] += number
    if (outgoing > numbers).any():
        print('attempt to move more pieces than owned\n')
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
    output = []
    n_max = numbers.max()
    for o_row, n_row in zip(owners, numbers):
        form = ''
        for o, n in zip(o_row, n_row):
            c = min(70 + n*185//n_max, 255)
            b = min(2*c, 255)
            form += ('\x1b[48;2;%d;%d;%dm' % (c,c,b)) + '%3d\x1b[0m'
        output.append(form % tuple(o_row))
        if print_numbers:
            output.append('%3d'*len(n_row) % tuple(n_row))
    print('\n'.join(output))


def game17(players, display_board=True, display_counts=False,
           board_size=14, num_rounds=50):
    """
    Play a game of Game 17.

    Parameters
    ----------
    players : list of functions
        A function for each player of the game.
    display_board : bool, optional
        Whether to display the board after each turn. The default is True.
    display_counts : bool, optional
        Whether to display counts if displaying the board.
        The default is False.

    Returns
    -------
    scores : dict of ints to ints
        The score of each player with a non-zero score.
    times : dict of ints to floats
        The average time (seconds) that calls to that player's function took

    """
    owners, numbers = create_board(board_size)
    all_owners = list(set(owners.flatten()))
    np.random.shuffle(all_owners)
    num_players = len(players)
    times = defaultdict(list)
    for round in range(num_rounds):
        for owner in all_owners:
            if owner not in set(owners.flatten()):
                continue
            if owner < num_players:
                safe_owners = np.array(owners)
                safe_numbers = np.array(numbers)
                start = time.process_time()
                moves = players[owner](owner, safe_owners, safe_numbers)
                end = time.process_time()
                times[owner].append(end - start)
            else:
                moves = make_moves_zombie(owner, owners, numbers)
            update_board(owner, moves, owners, numbers)
            num_players_left = len(set(owners[numbers > 0].flatten()))
            if display_board:
                print('round', round, 'player', owner)
                print_board(owners, numbers, display_counts)
                time.sleep(1 / num_players_left)
            if num_players_left == 1:
                break
        if num_players_left == 1:
            break
    scores = {o:(owners == o).sum() for o in np.unique(owners)}
    for owner in times:
        times[owner] = sum(times[owner]) / len(times[owner])
    return scores, times


if __name__ == '__main__':
    # This code plays a round of Game 17 and displays the result.
    scores, times = game17([make_moves], True)
    scores = pd.DataFrame(scores, index=['score'])
    print()
    print(scores.transpose())
    times = pd.DataFrame(times, index=['times'])
    print()
    print(times.transpose())