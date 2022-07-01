import os
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
import json
import time

import pandas as pd
import numpy as np

from .game17 import (
        print_board, apply_diff, board_diff, create_board, update_board)
from .zombie import make_moves as make_moves_zombie


def replay(game, display_counts=False, colours=None):
    """
    Display a single game to the screen

    Parameters
    ----------
    game : game structure
        Record of a game
    display_counts : bool
        Whether to display counts if displaying the board.
        The default is False.

    """
    owners = np.array(game['owners'])
    numbers = np.array(game['numbers'])
    diffs = game['diffs']

    print("let's go")
    print_board(owners, numbers, colours, display_counts)
    print()
    display_size = numbers.shape[0] + 2
    if display_counts and not colours:
        display_size += numbers.shape[0]
    for diff in diffs:
        apply_diff(numbers, diff['numbers'])
        apply_diff(owners, diff['owners'])
        print(f"\u001b[{display_size}A\u001b[2K"
              f"round {diff['round']}, player {diff['owner']}")
        print_board(owners, numbers, colours, display_counts)
        print()
        num_players_left = len(set(owners[numbers > 0].flatten()))
        time.sleep(1 / num_players_left)
    scores = pd.DataFrame(
            {o: (owners == o).sum() for o in np.unique(owners)},
            index=['squares'])
    print(scores.transpose())


def single(movers, board_size=14, num_rounds=50,
           display_counts=False, colours=None):
    'Run a single game of game17 and display to the terminal'
    scores, times, record = game17(
        movers, board_size=board_size, num_rounds=num_rounds)
    replay(record, display_counts, colours)
    times = pd.DataFrame(times, index=['times'])
    print()
    print(times.transpose())


# thanks https://stackoverflow.com/a/27050186
class NumPyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumPyEncoder, self).default(obj)


def round_robin(movers, output_directory, board_size=14, num_rounds=50,
                time_threshold=0.01, group=None):
    'Run a round-robin competition and dump results to files'
    # create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # play the games
    out_dir = Path(output_directory)
    outcomes = defaultdict(list)
    max_time = Counter()
    banned = set()
    # round robin, player vs player
    for player1, player2 in combinations(movers, 2):
        # if either player is banned, skip it
        if player1 in banned or player2 in banned:
            continue
        competitors = {player1: movers[player1], player2: movers[player2]}
        scores, times, record = game17(
            competitors, board_size=board_size, num_rounds=num_rounds)

        # save the record of the game
        with open(out_dir / f'{player1} vs {player2}.json', 'w') as mf:
            json.dump(record, mf, cls=NumPyEncoder)
        # if player takes more than 0.01 seconds, ban them
        for player in player1, player2:
            if time_threshold > 0 and times[player] > time_threshold:
                banned.add(player)
            max_time[player] = max(max_time[player], times[player])
        # save the outcomes
        for player, score in scores.items():
            if player in {player1, player2} and score == max(scores.values()):
                outcomes[frozenset((player1, player2))].append(player)

    # expunge the banned
    for the_banned in banned:
        for game in tuple(outcomes.keys()):
            if the_banned in game:
                del outcomes[game]

    # print game-by-game results
    if group:
        group = f'-{group}'
    else:
        group = ''
    with open(out_dir / f'round-robin{group}.txt', 'w') as rr:
        pretty_outcomes = {
            ' vs '.join(map(str, players)): ', '.join(map(str, winners))
            for players, winners in outcomes.items()}
        pretty_outcomes = pd.DataFrame(pretty_outcomes, index=['winner'])
        rr.write(pretty_outcomes.transpose().to_string() + '\n')

    # rank the movers
    winners = Counter(w for outcome in outcomes.values() for w in outcome)
    ranks = defaultdict(set)
    for player, games in winners.items():
        ranks[games].add(player)
    ranks = [ranks[g] for g in sorted(ranks, reverse=True)]
    if set(movers) - set(winners) - banned:
        ranks.append(set(movers) - set(winners) - banned)
    if banned:
        ranks.append(banned)

    # print summary
    with open(out_dir / f'round-robin-summary{group}.txt', 'w') as summary:
        winners = pd.DataFrame(
            {p: [str(winners.get(p, 'banned' if p in banned else 0)),
                 max_time[p]]
             for p in movers}, index=['games won', 'max time'])
        summary.write(winners.transpose().to_string() + '\n')

    return ranks


def battle_royale(movers, output_directory, num_games=100, board_size=14,
                  num_rounds=50, time_threshold=0.01):
    'Run multiple battle royale competitions and dump the results files'
    os.makedirs(output_directory, exist_ok=True)
    out_dir = Path(output_directory)
    banned = set()
    movers = dict(movers)
    victories = Counter()
    max_time = Counter()
    for i in range(num_games):
        scores, times, record = game17(
            movers, board_size=board_size, num_rounds=num_rounds)

        with open(out_dir / f'battle-royale-{i}.json', 'w') as mf:
            json.dump(record, mf, cls=NumPyEncoder)
        for player, ptime in times.items():
            if time_threshold > 0 and ptime > time_threshold:
                del movers[player]
                banned.add(player)
            max_time[player] = max(max_time[player], ptime)
        for player, score in scores.items():
            if player in movers and score == max(scores.values()):
                victories[player] += 1

    # expunge the banned
    for the_banned in banned:
        del victories[the_banned]

    # rank the movers
    ranks = defaultdict(set)
    for player, games in victories.items():
        ranks[games].add(player)
    ranks = [ranks[g] for g in sorted(ranks, reverse=True)]
    if set(movers) - set(victories) - banned:
        ranks.append(set(movers) - set(victories) - banned)
    if banned:
        ranks.append(banned)

    # print summary
    with open(out_dir / 'battle-royale-summary.txt', 'w') as br:
        winners = pd.DataFrame(
            {p: [str(victories.get(p, 'banned' if p in banned else 0)),
                 max_time[p]]
             for p in set(movers) | banned}, index=['games won', 'max time'])
        br.write(winners.transpose().to_string() + '\n')

    return ranks


def vs_zombies(movers, num_games=100, board_size=14, num_rounds=50):
    'Run multiple competitions and return number of wins'
    if len(movers) != 1:
        raise ValueError(
                f'vs_zombies passed {len(movers)} players. Should only be one')
    victories = Counter()
    max_time = Counter()
    for i in range(num_games):
        scores, times, record = game17(
            movers, board_size=board_size, num_rounds=num_rounds)

        for player, score in scores.items():
            if player in movers and score == max(scores.values()):
                max_time[player] = max(max_time[player], times[player])
                victories[player] += 1

    return victories, max_time


def game17(players, board_size=14, num_rounds=50):
    """
    Play a game of Game 17.

    Parameters
    ----------
    players : dict of functions
        A function for each player of the game. Keys are player numbers.
    display_board : bool, optional
        Whether to display the board after each turn. The default is True.
    display_counts : bool, optional
        Whether to display counts if displaying the board.
        The default is False.

    Returns
    -------
    scores : dict of ints to ints
        The score of each player with a non-zero score.
    times : dict of ints to floats
        The average time (seconds) that calls to that player's function took

    """
    owners, numbers = create_board(board_size)
    record = {'owners': np.array(owners),
              'numbers': np.array(numbers),
              'diffs': []}
    all_owners = list(set(owners.flatten()))
    np.random.shuffle(all_owners)
    movers = {}
    for owner, get_mover in players.items():
        movers[owner] = get_mover(
                owner=owner, owners=owners, numbers=numbers,
                turn_order=all_owners, num_rounds=num_rounds)
    times = defaultdict(list)
    for round in range(num_rounds):
        for owner in all_owners:
            if owner not in set(owners.flatten()):
                continue
            if owner in movers:
                safe_owners = np.array(owners)
                safe_numbers = np.array(numbers)
                try:
                    start = time.process_time()
                    moves = movers[owner](safe_owners, safe_numbers)
                    end = time.process_time()
                except KeyboardInterrupt:
                    raise
                except Exception:
                    moves = []
                    end = time.process_time()
                times[owner].append(end - start)
            else:
                rounds_left = num_rounds - round - 1
                moves = make_moves_zombie(owner, rounds_left, owners, numbers)
            before_owners = np.array(owners)
            before_numbers = np.array(numbers)
            try:
                safe_owners = np.array(owners)
                safe_numbers = np.array(numbers)
                update_board(owner, moves, owners, numbers)
            except KeyboardInterrupt:
                raise
            except Exception:
                owners = safe_owners
                numbers = safe_numbers
                print(f'skipping player {owner}, '
                      'because they broke update_board')
            record['diffs'].append({
                'round': round,
                'owner': owner,
                'owners': board_diff(before_owners, owners),
                'numbers': board_diff(before_numbers, numbers)})
            num_players_left = len(set(owners[numbers > 0].flatten()))
            if num_players_left == 1:
                break
        if num_players_left == 1:
            break
    scores = {o: (owners == o).sum() for o in np.unique(owners)}
    for owner in players:
        if owner in times:
            times[owner] = sum(times[owner]) / len(times[owner])
        else:
            times[owner] = -1
    return scores, times, record
