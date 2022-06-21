
import numpy as np

from .game17 import find_owned_pieces


def make_moves(owner, owners, numbers):
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
