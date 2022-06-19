# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:18:04 2022

@author: Ben Kaehler
"""

__version__ = 1.0

import os
import sys
import time
from collections import defaultdict, Counter
from importlib import import_module, reload
from itertools import combinations
from pathlib import Path
import json

import numpy as np
import pandas as pd
import click

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
            form += ('\x1b[48;2;%d;%d;%dm' % (c,c,b)) + '%3d\x1b[0m'
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


def game17(players, display_board=False, display_counts=False,
           board_size=14, num_rounds=50):
    """
    Play a game of Game 17.

    Parameters
    ----------
    players : dict of functions
        A function for each player of the game. Keys are player numbers.
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
    record = {'owners' : np.array(owners),
              'numbers' : np.array(numbers),
              'diffs' : []}
    all_owners = list(set(owners.flatten()))
    np.random.shuffle(all_owners)
    times = defaultdict(list)
    for round in range(num_rounds):
        for owner in all_owners:
            if owner not in set(owners.flatten()):
                continue
            if owner in players:
                safe_owners = np.array(owners)
                safe_numbers = np.array(numbers)
                try:
                    start = time.process_time()
                    moves = players[owner](owner, safe_owners, safe_numbers)
                    end = time.process_time()
                except KeyboardInterrupt:
                    raise
                except Exception:
                    moves = []
                    end = time.process_time()
                times[owner].append(end - start)
            else:
                moves = make_moves_zombie(owner, owners, numbers)
            before_owners = np.array(owners)
            before_numbers = np.array(numbers)
            update_board(owner, moves, owners, numbers)
            record['diffs'].append({
                'round' : round,
                'owner' : owner,
                'owners' : board_diff(before_owners, owners),
                'numbers' : board_diff(before_numbers, numbers)})
            num_players_left = len(set(owners[numbers > 0].flatten()))
            if display_board:
                print('round %d, player %d' % (round, owner))
                print_board(owners, numbers, display_counts)
                time.sleep(1 / num_players_left)
            if num_players_left == 1:
                break
        if num_players_left == 1:
            break
    scores = {o:(owners == o).sum() for o in np.unique(owners)}
    for owner in players:
        if owner in times:
            times[owner] = sum(times[owner]) / len(times[owner])
        else:
            times[owner] = -1
    return scores, times, record


# thanks https://stackoverflow.com/a/27050186
class NumPyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumPyEncoder, self).default(obj)


def vs_zombies(num_games, movers, player_modules, board_size, num_rounds):
    'Run multiple competitions and return number of wins'
    movers = dict(movers)
    victories = Counter()
    max_time = Counter()
    for i in range(num_games):
        for player, module in player_modules.items():
            reload(module)

        scores, times, record = game17(
            movers, board_size=board_size, num_rounds=num_rounds)

        max_time[player] = max(max_time[player], times[player])
        for player, score in scores.items():
            if player in movers and score == max(scores.values()):
                victories[player] += 1
        
    return victories, max_time
    

@click.command()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-k', '--kind-to-time-hogs', is_flag=True)
@click.option('-g', '--num-games', default=100)
@click.argument('players', nargs=-1, type=click.Path(exists=True))
@click.argument('output_directory', nargs=1, type=click.Path(exists=True, file_okay=False))
def rank(players, output_directory, verbose, display_counts,
                board_size, num_rounds, kind_to_time_hogs, num_games):
    '''
    Play Game 17, battle royale, followed by round-robin run-off competitions.

    Parameters
    ----------
    players : Python files
        Python files containing make moves functions. Must be in working dir.
    output_directory : directory
        Directory into which results should be written.
    verbose : bool
        Display games to screen.
    display_counts : bool
        Display couts in displayed games.
    board_size : int
        Size of the boaud [default=14].
    num_rounds : int
        Number of rounds to play [default=50].
    kind_to_time_hogs : bool
        Don't ban players whose code takes more than 0.01 s.

    Returns
    -------
    int
        Non-zero on failure.

    '''
    # load the players
    player_modules = {}
    movers = {}
    bad_modules = set()
    with open(Path(output_directory) / 'players.txt', 'w') as player_file:
        for i, player in enumerate(players, 1):
            player_file.write(f'{player} is player {i}\n')
            try:
                player_module = import_module(player[:-3])
                movers[i] = player_module.make_moves
                player_modules[i] = player_module
            except TypeError as err:
                if 'relative import' in err:
                    print(player, 'must be in the working directory',
                          file=sys.stderr)
                    return -1
                raise
            except KeyboardInterrupt:
                raise
            except Exception as err:
                bad_modules.add(i)
    

    # make a record of the players whose modules did not load
    with open(Path(output_directory) / 'players_that_failed_on_import.txt', 'w') as fh:
        fh.write(', '.join(map(str, bad_modules)) + '\n')
    
    with open(Path(output_directory) / 'vs_zombies.txt', 'w') as fh:
        fh.write('player\tnum_wins\tmax_time\n')
        print('player\tnum_wins\tmax_time')
        for player in movers:
            one_mover = {0 : movers[player]}
            one_module = {0 : player_modules[player]}
            victories, max_time = vs_zombies(
                    num_games, one_mover, one_module, board_size, num_rounds)
            print(f'{player}\t{victories[0]}\t{max_time[0]}')
            fh.write(f'{player}\t{victories[0]}\t{max_time[0]}\n')
        
    return 0
        

if __name__ == '__main__':
    sys.exit(rank())
        
    
            
            
        
