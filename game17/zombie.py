
import numpy as np

from .game17 import find_owned_pieces


def make_moves(owner, rounds_left, owners, numbers):
    """
    Zombie mover. Moves each owned piece in a random direction.

    Parameters
    ----------
    owner : int
        Player number.
    rounds_left : int
        Maximum possible rounds left after this one.
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
    moves = []
    for pieces in owned_pieces:
        coords = pieces[:2]
        count = pieces[2]
        to_move = np.random.multinomial(count, [0.25]*4)
        for i in range(4):
            if to_move[i] > 0:
                move = (coords, 'nsew'[i], to_move[i])
                moves.append(move)
    return moves
