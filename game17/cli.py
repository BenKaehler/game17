import importlib.util
import sys
import json
import os
from pathlib import Path

import click
import pandas as pd

from game17 import game_runners, basic_mover


@click.group()
def cli():
    pass


@cli.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.argument('game', type=click.File())
@click.argument('colours', nargs=-1, type=str)
def replay(colours, game, display_counts):
    'Replay a game of Game 17 on the terminal'
    game = json.load(game)
    colours = {int(i): n for i, n in (c.split(':', 1) for c in colours)}
    game_runners.replay(game, display_counts, colours)


def import_module(filename):
    # thank you https://stackoverflow.com/q/67631
    module_path = Path(filename).resolve()
    module_name = module_path.stem
    spec = importlib.util.spec_from_file_location(
        module_name, str(module_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_modules(players, players_file):
    'load the players'
    movers = {}
    colours = {}
    bad_modules = set()
    for i, player in enumerate(players, 1):
        if ':' in player:
            player, colour = player.split(':', 1)
        else:
            colour = None
        players_file.write(f'{player} is player {i}\n')
        try:
            player_module = import_module(player)
            if hasattr(player_module, 'make_moves'):
                movers[i] = basic_mover.get_mover_factory(
                        player_module.make_moves)
            else:
                movers[i] = player_module.get_mover
            if colour:
                colours[i] = colour
        except TypeError as err:
            if 'relative import' in err:
                print(player, 'must be in the working directory',
                      file=sys.stderr)
                return -1
            raise
        except KeyboardInterrupt:
            raise
        except Exception as err:
            bad_modules.add(i)
            print(f'Player {i} failed to load:')
            print(err)
    return movers, colours, bad_modules


@cli.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-k', '--kind-to-time-hogs', is_flag=True)
@click.option('-g', '--num-games', default=100)
@click.option('-p', '--players-file',
              type=click.File('w'), default='players.txt')
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
    movers, _, bad_modules = load_modules(players, players_file)

    # create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # make a record of the players whose modules did not load
    with open(Path(output_directory) /
              'players_that_failed_on_import.txt', 'w') as fh:
        fh.write(', '.join(map(str, bad_modules)) + '\n')

    ranks = game_runners.battle_royale(
            movers, output_directory, num_games, board_size,
            num_rounds, kind_to_time_hogs)

    fine_ranks = []
    for group, rank in enumerate(ranks):
        if len(rank) == 1:
            fine_ranks.append(rank)
            continue
        rank_movers = {p: m for p, m in movers.items() if p in rank}
        fine_rank = game_runners.round_robin(
            rank_movers, output_directory, board_size, num_rounds,
            kind_to_time_hogs, group)
        fine_ranks.extend(fine_rank)

    with open(Path(output_directory) / 'ranks.txt', 'w') as rf:
        ranks = pd.DataFrame(
            {i: ', '.join(map(str, r)) for i, r in enumerate(fine_ranks)},
            index=['players'])
        rf.write(ranks.transpose().to_string() + '\n')

    return 0


@cli.command()
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-k', '--kind-to-time-hogs', is_flag=True)
@click.option('-g', '--num-games', default=100)
@click.option('-p', '--players-file',
              type=click.File('w'), default='players.txt')
@click.argument('players', nargs=-1, type=click.Path(exists=True))
@click.argument('output_directory', nargs=1, type=click.Path(file_okay=False))
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
    movers, _, bad_modules = load_modules(players, players_file)

    # create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # make a record of the players whose modules did not load
    with open(Path(output_directory) /
              'players_that_failed_on_import.txt', 'w') as fh:
        fh.write(', '.join(map(str, bad_modules)) + '\n')

    with open(Path(output_directory) / 'vs-zombies.txt', 'w') as fh:
        fh.write('player\tnum_wins\tmax_time\n')
        for player in movers:
            one_mover = {0: movers[player]}
            victories, max_time = game_runners.vs_zombies(
                    one_mover, num_games, board_size, num_rounds)
            fh.write(f'{player}\t{victories[0]}\t{max_time[0]}\n')

    return 0


@cli.command()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-c', '--display-counts', is_flag=True)
@click.option('-s', '--board-size', type=int, default=14)
@click.option('-r', '--num-rounds', type=int, default=50)
@click.option('-p', '--players-file',
              type=click.File('w'), default='players.txt')
@click.argument('players', nargs=-1, type=str)  # todo make custom type
def single(players, verbose, display_counts, board_size,
           num_rounds, players_file):
    'Play a single game of game17'
    # load the players
    movers, colours, bad_modules = load_modules(
            players, players_file)
    game_runners.single(
            movers, board_size, num_rounds, display_counts, colours)
