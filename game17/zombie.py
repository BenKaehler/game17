
import numpy as np

from .game17 import find_owned_pieces


def make_moves(owner, rounds_left, owners, numbers):
    """
    T800 mover. Initially moves each owned piece in a random direction. Once
    the android owns more than 2 squares it changes tactic to actively target
    its neighbours by sending count + 1 to largest rival in descending order.

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
    
    owned_squares = find_owned_pieces(owner, owners, numbers)
    moves = []
    for squares in owned_squares:
        coords = squares[:2]
        count = squares[2]
        rivals = find_local_rivals(owner, owners, numbers, coords)
        rival_squares = sorted(rivals, key=lambda t: t[::-1],reverse=True)
        if len(owned_squares) == 1:
            to_move = np.random.multinomial(count, [0.25]*4)
            for i in range(4):
                if to_move[i] > 0:
                    move = (coords, 'nsew'[i],to_move[i])
                    moves.append(move)
        
        elif count< 40:            
            for rival in rival_squares:
                rival_count = rival[1]
                rival_direction = rival[0]
                if rival_count <= count:
                    move = (coords, rival_direction, count)
                    moves.append(move)
                    count = 0
        else:
            for rival in rival_squares:
                rival_count = rival[1]
                rival_direction = rival[0]
                if rival_count < count:
                    move = (coords, rival_direction, (rival_count+1))
                    moves.append(move)
                    count -= (rival_count+1)
    return moves

def find_local_rivals(owner, owners, numbers, coords):
    """
    Finds local rivals for given input coordinates.
    Parameters
    ----------
    owner : int
        Owner to find the pieces for.
    owners : square array of ints
        Owners of squares.
    numbers : square array of ints
        Number of pieces in squares.
    coords : 1 x 2 numpy array
        Coordinates to find local rivals.

    Returns
    -------
    List of tuples
        Each tuple contains a string giving the direction of a rival
        ('n', 's', 'e', or 'w'), and an int giving the number of pieces in the
        rival square.

    """
    
    board_size = owners.shape[0]
    ix = (owner != owners)
    row,col = coords
    rival_direction,rival_number = [],[]
    #bool array of immediate local squares relative to inout coords
    row_n, row_s = (row-1)%board_size,(row+1)%board_size
    col_e, col_w = (col+1)%board_size, (col-1)%board_size
    rival = np.array(ix[[row_n,row,row_s,row], [col,col_e,col,col_w]])#n,e,s,w
 
    if rival[0]:
        rival_direction.append('n')
        rival_number.append(numbers[row_n,col])
    if rival[1]:
        rival_direction.append('e')
        rival_number.append(numbers[row,col_e])
    if rival[2]:
        rival_direction.append('s')
        rival_number.append(numbers[row_s,col])
    if rival[3]:
        rival_direction.append('w')
        rival_number.append(numbers[row,col_w])
        
    return list(zip(rival_direction, rival_number)) 