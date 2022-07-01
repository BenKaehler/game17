import numpy as np

from game17 import find_owned_pieces, destination


def zombie_strategy(neighbours, count):
    'card counting zombie'
    p = np.array(neighbours, dtype=float) + 0.01
    p /= p.sum()
    while ((p*count > 0) & (p*count < neighbours)).sum() > 0:
        p[p*count < neighbours] = 0
        if p.sum() > 0:
            p /= p.sum()
        else:
            break
    return p


def make_moves(owner, rounds_left, owners, numbers):
    """
    A slightly smarter zombie.

    Parameters
    ----------
    owner : int
        Your player number.
    rounds_lift : int
        Maximum possible number of rounds to be played after this one.
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
    board_size = numbers.shape[0]
    moves = []
    for i, j, count in find_owned_pieces(owner, owners, numbers):
        neighbours = [numbers[tuple(destination((i, j), d, board_size))]
                      for d in 'nsew']
        p = zombie_strategy(neighbours, count)
        if p.sum() > 0:
            to_move = np.random.multinomial(count, p)
            for k in range(4):
                if to_move[k] > 0:
                    move = ((i, j), 'nsew'[k], to_move[k])
                    moves.append(move)
    return moves
