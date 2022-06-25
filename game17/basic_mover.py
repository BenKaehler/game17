def get_mover_factory(make_moves):
    'creates a get_mover function for a basic make_moves function'
    def get_mover(owner=None, owners=None, numbers=None,
                  turn_order=None, num_rounds=None):
        return BasicMover(make_moves, owner, num_rounds)
    return get_mover


class BasicMover(object):
    def __init__(self, make_moves, owner, num_rounds):
        self.make_moves = make_moves
        self.owner = owner
        self.rounds_left = num_rounds

    def __call__(self, owners, numbers):
        self.rounds_left -= 1
        moves = self.make_moves(self.owner, self.rounds_left, owners, numbers)
        return moves
