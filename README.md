# game17

## Installation

```
pip install git+https://github.com/BenKaehler/game17.git
```

## Usage

### Python interface

The Python interface is useful for experimenting, and works if all you have access to is a Python console.

First of all, check that you're in the demo directory.

```python
import os
os.getcwd()
```

The output should end in `game17/demo` (or `game17\demo`).

Now, import `game17` and the working stub.

```python
import game17
import stub
```

You have to create a dictionary of players to feed to `game17`. The keys are the player numbers. If you've got a basic player that implements `make_moves`, you do it as follows.

```python
players = {1: game17.get_mover_factory(stub.make_moves)}
```

Now you're ready to play a single game.

```python
game17.single(players)
```

You can play 100 games against zombies to get a statistical picture of how good your player is.

```python
wins, times = game17.vs_zombies(players)
```

After you've run that, `wins` will contain a dictionary counting the wins of the players and `times` will contain a dictionary of the maximum average time your player took.

To compete, you can run a battle royale, where all players compete against all players multiple times, or you can run a round-robin competition. We only have one player, so let's play it against itself.

```python
players = {1: game17.get_mover_factory(stub.make_moves),
	   2: game17.get_mover_factory(stub.make_moves)}
```

Now run the battle royale

```python
ranking = game17.battle_royale(players, 'battle-royale-output-directory')
```

`battle_royale` puts the resulting rankings in ranking, but most of the copious information that it produces will now be in a directory called "battle-royale-output-directory".

The round robin works the same way.

```python
ranking = game17.round_robin(players, 'round-robin-output-directory')
```

It's less-copious output should now be in a directory called "round-robin-output-directory". Although, if you've got lots of players, the amount of output (and run time) grows like the number of pairs.

Finally, you can replay any of the games from the battle royale or round robin. You have to load them first.

```python
import json
with open('battle-royale-output-directory/battle-royale-0.json') as brf:
    game = json.load(brf)
game17.replay(game)
```

There are lots of options for these functions, so you can change the board size, the number of rounds, and other things. You can explore them in the usual way using Python help and introspection.

### Now in colour!

By default, `game17` displays boards with the owner displayed as a number and the number of pieces indicated by the shade of purple of each square.

You can instead now choose a colour for each player, and the numbers will instead show the number of pieces in each square. All zombies will be `game17` purple.

Here is an example.

```python
import game17
import stub

players = {1: game17.get_mover_factory(stub.make_moves),
           2: game17.get_mover_factory(stub.make_moves),
           3: game17.get_mover_factory(stub.make_moves),
           4: game17.get_mover_factory(stub.make_moves)}

colours = {1: 'orange',
           2: 'green',
           3: 'xkcd:baby shit green',
           4: 'xkcd:baby shit brown'}

game17.single(players, colours=colours, board_size=3, num_rounds=10)
```

The colour names must be [`matplotlib` color names](https://matplotlib.org/stable/gallery/color/named_colors.html).

You can also add colour to single games or replays on the command line (see below).

```bash
game17 single stub.py:orange stub.py:green -s 2
```

For replays, colours must be assigned by player number.

```bash
game17 replay ranking-output-directory/battle-royale-0.json 1:orange 2:green
```

### Smarter Zombies

You can add as many T800s as you have room for in your game by adding them like ordinary players.

```python
import game17
from game17 import T800
import stub

players = {1: game17.get_mover_factory(stub.make_moves),
           2: game17.get_mover_factory(T800.make_moves)}

colours = {1: 'orange', 2: 'xkcd:deep purple'}

game17.single(players, colours=colours)
```

You can add T800s to your command line games with the `-T` or `--num-T800s` option.

### Command Line Interface

The command line interface is a little more powerful (and actually easier to use) than the Python interface. It's what a marker would use to assess a collection of `game17` players.

There is a demo player in the demo directory, so

```bash
cd demo  # make demo your working directory
```

To run a single game:

```bash
game17 single stub.py
```

To play players against zombies (repeatedly):

```bash
game17 vs-zombies stub.py vs-zombies-output-directory
```

To rank a collection of players:

```bash
game17 rank stub.py stub.py ranking-output-directory
```

To replay a game:

```bash
game17 replay ranking-output-directory/battle-royale-0.json
```

For help:

```bash
game17 --help
```

or, eg.,

```bash
game17 single --help
```

## Rules

Game 17 is a game for 0 to 196 players. It is played on a 14 x 14 checkerboard. The edges of the checkerboard are considered linked, so squares on the right edge are adjacent to corresponding squares on the left edge, and similarly for squares on the top and bottom of the board.

### Setup

At the start of the game, each square contains four pieces. Each player is given a single square and the pieces on it. Square allocations are random. If there are less than 196 players, any squares and pieces not already allocated are given to zombies. Zombies are computer-controlled players.

Play is turn based, and each player gets one turn each round. The order of turns within a round is decided randomly and fixed before the start of the game.

### Game Play

When it is their turn, a player can move each piece in their possession to an adjacent square or leave it where it is. Pieces can be moved independently. At the end of a turn, if a square contains pieces owned by more than one player, all of the pieces become the possession of the owner of the majority of those pieces. A tie is resolved by a fair coin toss. In such a fashion players can gain and lose pieces.

A square is said to be owned by the player that owns the pieces in that square, or whoever most recently owned it if it is empty.

When it is a zombie???s turn, the zombie moves its pieces randomly. It always moves all of its pieces.

### End of Play

Play finishes as soon as all of the pieces belong to one player or after all players have had fifty turns.

### Winning

The player or zombie who owns the most squares at the end of play wins. All of the players that tie for first win.

## Creating New Players

### Basic Player

A basic player must be saved in a Python file that contains at least a function with the following signature:

```python
def make_moves(owner, rounds_left, owners, numbers):
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
```

See `game17/zombie.py` for a working, if not terribly intelligent, example.

### Advanced Player

You can make a stateful player by creating a Python file that contains a function called `get_mover` with the signature

```python
def get_mover(owner=None, owners=None, numbers=None,
              turn_order=None, num_rounds=None):
    'Get a callable object with the signature [callable](owners, numbers)'
```

Your implementation of `get_mover` must return a callable object that takes just two inputs, `owners` and `numbers`.

`get_mover` is called just once at the start of each game, giving the player its owner number and other details about the game. Then the callable object that it returns must respond to the state of the board in its turn.

A zombie stateful player is given as an example in `demo/stub_advanced.py`.

Advanced players are detected automatically on the command line. For the Python interface, the example given above is now easier.


```python
import game17
import stub_advanced

players = {1: stub_advanced.get_mover,
           2: stub_advanced.get_mover,
           3: stub_advanced.get_mover,
           4: stub_advanced.get_mover}

colours = {1: 'orange',
           2: 'green',
           3: 'xkcd:baby shit green',
           4: 'xkcd:baby shit brown'}

game17.single(players, colours=colours, board_size=3, num_rounds=10)
```

You can mix and match basic and advanced players.
