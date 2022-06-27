from game17.zombie import make_moves as make_moves_zombie


def get_mover(owner=None, owners=None, numbers=None,
              turn_order=None, num_rounds=None):
    'Get a callable object with the signature [callable](owners, numbers)'
    return AdvancedMoverStub(owner, num_rounds)


class AdvancedMoverStub(object):
    'A callable class that allows for a stateful mover'

    def __init__(self, owner, num_rounds):
        'Initialise an object - must take all required info as input'
        self.owner = owner
        self.rounds_left = num_rounds

    def __call__(self, owners, numbers):
        'Stateful replacement for the basic make_moves function'
        self.rounds_left -= 1
        moves = make_moves_zombie(
                self.owner, self.rounds_left, owners, numbers)
        return moves
