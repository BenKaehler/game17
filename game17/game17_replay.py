import sys
import time
import json

import click
import numpy as np
import pandas as pd

from game17_ranking import print_board, update_board, apply_diff

@click.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.argument('game', type=click.File())
def replay(game, display_counts):
    'replay a game of Game 17 on the terminal'
    game = json.load(game)
    owners = np.array(game['owners'])
    numbers = np.array(game['numbers'])
    diffs = game['diffs']

    print_board(owners, numbers, display_counts)
    print()
    for diff in diffs:
        owner = diff['owner']
        apply_diff(numbers, diff['numbers'])
        apply_diff(owners, diff['owners'])
        print(f"round {diff['round']}, player {diff['owner']}")
        print_board(owners, numbers, display_counts)
        print()
        num_players_left = len(set(owners[numbers > 0].flatten()))
        time.sleep(1 / num_players_left)
    scores = pd.DataFrame(
            {o:(owners == o).sum() for o in np.unique(owners)},
            index=['squares'])
    print(scores.transpose())
    return 0

if __name__ == '__main__':
    sys.exit(replay())
