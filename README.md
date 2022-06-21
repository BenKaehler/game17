# game17

## Installation

```
pip install git+https://github.com/BenKaehler/game17.git
```

## Usage

There is a demo player in the demo directory, so

```
cd demo  # make demo your working directory
```

To run a single game:

```
game17 single stub.py
```

To play players against zombies (repeatedly):

```
game17 vs-zombies stub.py vs-zombies-output-directory
```

To rank a collection of players:

```
game17 rank stub.py stub.py ranking-output-directory
```

To replay a game:

```
game17 replay ranking-output-directory/battle-royale-0.json
```

For help:

```
game17 --help
```

or, eg.,

```
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

When it is a zombie’s turn, the zombie moves its pieces randomly. It always moves all of its pieces.

### End of Play

Play finishes as soon as all of the pieces belong to one player or after all players have had fifty turns.

### Winning

The player or zombie who owns the most squares at the end of play wins. All of the players that tie for first win.
