from importlib import import_module
import sys
import json
import os
from pathlib import Path

import click
import pandas as pd

from game17 import game_runners


@click.group()
def cli():
    pass


@cli.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.argument('game', type=click.File())
def replay(game, display_counts):
    'replay a game of Game 17 on the terminal'
    game = json.load(game)
    game_runners.replay(game)


def load_modules(players, players_file):
    'load the players'
    player_modules = {}
    movers = {}
    bad_modules = set()
    for i, player in enumerate(players, 1):
        players_file.write(f'{player} is player {i}\n')
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
        except Exception:
            bad_modules.add(i)
    return player_modules, movers, bad_modules


@cli.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-k', '--kind-to-time-hogs', is_flag=True)
@click.option('-g', '--num-games', default=100)
@click.option('-p', '--players-file', type=click.File('wb'),
              default='players.txt')
@click.argument('players', nargs=-1, type=click.Path(exists=True))
@click.argument('output_directory', nargs=1, type=click.Path(file_okay=False))
def rank(players, output_directory, display_counts, board_size, num_rounds,
         kind_to_time_hogs, num_games, players_file):
    '''
    Play Game 17, battle royale, followed by round-robin run-off competitions.

    Parameters
    ----------
    players : Python files
        Python files containing make moves functions. Must be in working dir.
    output_directory : directory
        Directory into which results should be written.
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
    player_modules, movers, bad_modules = load_modules(players, players_file)

    # create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # make a record of the players whose modules did not load
    with open(Path(output_directory) /
              'players_that_failed_on_import.txt', 'w') as fh:
        fh.write(', '.join(map(str, bad_modules)) + '\n')

    ranks = game_runners.battle_royale(
            num_games, movers, player_modules, board_size,
            num_rounds, kind_to_time_hogs, output_directory)

    fine_ranks = []
    for group, rank in enumerate(ranks):
        if len(rank) == 1:
            fine_ranks.append(rank)
            continue
        rank_movers = {p: m for p, m in movers.items() if p in rank}
        fine_rank = game_runners.round_robin(
            rank_movers, player_modules, board_size, num_rounds,
            kind_to_time_hogs, output_directory, group)
        fine_ranks.extend(fine_rank)

    with open(Path(output_directory) / 'ranks.txt', 'w') as rf:
        ranks = pd.DataFrame(
            {i: ', '.join(map(str, r)) for i, r in enumerate(fine_ranks)},
            index=['rank'])
        rf.write(ranks.transpose().to_string() + '\n')

    return 0


@cli.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-k', '--kind-to-time-hogs', is_flag=True)
@click.option('-g', '--num-games', default=100)
@click.option('-p', '--players-file', type=click.File('wb'),
              default='players.txt')
@click.argument('players', nargs=-1,
                type=click.Path(exists=True))
@click.argument('output_directory', nargs=1,
                type=click.Path(exists=True, file_okay=False))
def vs_zombies(players, output_directory, display_counts,
               board_size, num_rounds, kind_to_time_hogs, num_games,
               players_file):
    '''
    Play Game 17, battle royale, followed by round-robin run-off competitions.

    Parameters
    ----------
    players : Python files
        Python files containing make moves functions. Must be in working dir.
    output_directory : directory
        Directory into which results should be written.
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
    player_modules, movers, bad_modules = load_modules(players, players_file)

    # create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # make a record of the players whose modules did not load
    with open(Path(output_directory) /
              'players_that_failed_on_import.txt', 'w') as fh:
        fh.write(', '.join(map(str, bad_modules)) + '\n')

    with open(Path(output_directory) / 'vs_zombies.txt', 'w') as fh:
        fh.write('player\tnum_wins\tmax_time\n')
        print('player\tnum_wins\tmax_time')
        for player in movers:
            one_mover = {0: movers[player]}
            one_module = {0: player_modules[player]}
            victories, max_time = vs_zombies(
                    num_games, one_mover, one_module, board_size, num_rounds)
            print(f'{player}\t{victories[0]}\t{max_time[0]}')
            fh.write(f'{player}\t{victories[0]}\t{max_time[0]}\n')

    return 0


@cli.command()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-p', '--players-file',
              type=click.File('wb'), default='players.txt')
@click.argument('players', nargs=-1, type=click.Path(exists=True))
def single(players, verbose, display_counts, board_size, num_rounds,
           kind_to_time_hogs, num_games, players_file):
    # load the players
    player_modules, movers, bad_modules = load_modules(players, players_file)
    single(movers, player_modules, board_size, num_rounds, display_counts)
