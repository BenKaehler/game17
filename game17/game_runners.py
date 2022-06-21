from collections import defaultdict, Counter
from importlib import reload
from itertools import combinations
from pathlib import Path
import json
import time

import pandas as pd
import numpy as np

from game17 import print_board, game17, apply_diff


def replay(game, display_counts):
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

    print_board(owners, numbers, display_counts)
    print()
    for diff in diffs:
        apply_diff(numbers, diff['numbers'])
        apply_diff(owners, diff['owners'])
        print(f"round {diff['round']}, player {diff['owner']}")
        print_board(owners, numbers, display_counts)
        print()
        num_players_left = len(set(owners[numbers > 0].flatten()))
        time.sleep(1 / num_players_left)
    scores = pd.DataFrame(
            {o: (owners == o).sum() for o in np.unique(owners)},
            index=['squares'])
    print(scores.transpose())


def single(movers, player_modules, board_size, num_rounds,
           display_counts):
    'Run a single game of game17 and display to the terminal'
    for module in player_modules.values():
        reload(module)
    scores, times, record = game17(
        movers, board_size=board_size, num_rounds=num_rounds)
    replay(record, display_counts)
    scores = pd.DataFrame(scores, index=['score'])
    print()
    print(scores.transpose())
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


def round_robin(movers, player_modules, board_size, num_rounds,
                kind_to_time_hogs, output_directory, group):
    'Run a round-robin competition and dump results to files'
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
        # by kind and reload dodgy round counters
        for player in competitors:
            reload(player_modules[player])

        scores, times, record = game17(
            competitors, board_size=board_size, num_rounds=num_rounds)

        # save the record of the game
        with open(out_dir / f'{player1} vs {player2}.json', 'w') as mf:
            json.dump(record, mf, cls=NumPyEncoder)
        # if player takes more than 0.01 seconds, ban them
        for player in player1, player2:
            if not kind_to_time_hogs and times[player] > 0.01:
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
    with open(out_dir / f'round-robin-{group}.txt', 'w') as rr:
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
    with open(out_dir / f'round-robin-summary-{group}.txt', 'w') as summary:
        winners = pd.DataFrame(
            {p: [str(winners.get(p, 'banned' if p in banned else 0)),
                 max_time[p]]
             for p in movers}, index=['games won', 'max time'])
        summary.write(winners.transpose().to_string() + '\n')

    return ranks


def battle_royale(num_games, movers, player_modules, board_size, num_rounds,
                  kind_to_time_hogs, output_directory):
    'Run multiple battle royale competitions and dump the results files'
    out_dir = Path(output_directory)
    banned = set()
    movers = dict(movers)
    victories = Counter()
    max_time = Counter()
    for i in range(num_games):
        for player, module in player_modules.items():
            if player not in banned:
                reload(module)

        scores, times, record = game17(
            movers, board_size=board_size, num_rounds=num_rounds)

        with open(out_dir / f'battle-royale-{i}.json', 'w') as mf:
            json.dump(record, mf, cls=NumPyEncoder)
        if not kind_to_time_hogs:
            for player, ptime in times.items():
                if time > 0.01:
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


def vs_zombies(num_games, movers, player_modules, board_size, num_rounds):
    'Run multiple competitions and return number of wins'
    movers = dict(movers)
    victories = Counter()
    max_time = Counter()
    for i in range(num_games):
        for player, module in player_modules.items():
            reload(module)

        scores, times, record = game17(
            movers, board_size=board_size, num_rounds=num_rounds)

        max_time[player] = max(max_time[player], times[player])
        for player, score in scores.items():
            if player in movers and score == max(scores.values()):
                victories[player] += 1

    return victories, max_time
