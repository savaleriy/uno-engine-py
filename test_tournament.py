#!/usr/bin/env python3
"""
Test script for UNO Tournament System - All Formats
"""

import sys

sys.path.insert(0, ".")

from uno.engine.tournament import UNOTournament, TournamentFormat
from uno.bots import (
    RandomBot,
    WildFirstBot,
    WildLastBot,
    ZemtsevBot,
    WellBot,
    AkimVBot,
    ZhadnovBot,
    SkripkinBot,
    KintselBot,
)


def test_single_elimination():
    """Test single elimination tournament"""
    print("=" * 70)
    print("TEST 1: Single Elimination Tournament (8 players)")
    print("=" * 70)

    bots = [
        RandomBot("Random1", 1),
        RandomBot("Random2", 2),
        WildFirstBot("WildFirst1", 3),
        WildFirstBot("WildFirst2", 4),
        WildLastBot("WildLast1", 5),
        ZemtsevBot("Zemtsev", 6),
        WellBot("Helga", 7),
        AkimVBot("Akim", 8),
    ]

    tournament = UNOTournament(
        players=bots,
        games_per_match=20,  # Small for quick test
        format=TournamentFormat.SINGLE_ELIMINATION,
        seed=42,
    )

    winner = tournament.run_tournament()
    tournament.print_standings()

    return tournament


def test_double_elimination():
    """Test double elimination tournament"""
    print("\n" + "=" * 70)
    print("TEST 2: Double Elimination Tournament (6 players)")
    print("=" * 70)

    bots = [
        RandomBot("Random1", 1),
        WildFirstBot("WildFirst1", 2),
        WildLastBot("WildLast1", 3),
        ZemtsevBot("Zemtsev", 4),
        WellBot("Helga", 5),
        AkimVBot("Akim", 6),
    ]

    tournament = UNOTournament(
        players=bots,
        games_per_match=15,  # Small for quick test
        format=TournamentFormat.DOUBLE_ELIMINATION,
        seed=123,
    )

    winner = tournament.run_tournament()
    tournament.print_standings()

    return tournament


def test_round_robin():
    """Test round robin tournament"""
    print("\n" + "=" * 70)
    print("TEST 3: Round Robin Tournament (6 players)")
    print("=" * 70)

    bots = [
        RandomBot("Random1", 1),
        WildFirstBot("WildFirst1", 2),
        WildLastBot("WildLast1", 3),
        ZemtsevBot("Zemtsev", 4),
        WellBot("Helga", 5),
        AkimVBot("Akim", 6),
    ]

    tournament = UNOTournament(
        players=bots,
        games_per_match=10,  # Small for round robin (many matches)
        format=TournamentFormat.ROUND_ROBIN,
        seed=456,
    )

    winner = tournament.run_tournament()
    tournament.print_standings()
    tournament.print_tournament_stats()

    return tournament


def test_swiss():
    """Test Swiss system tournament"""
    print("\n" + "=" * 70)
    print("TEST 4: Swiss System Tournament (8 players, 4 rounds)")
    print("=" * 70)

    bots = [
        RandomBot("Random1", 1),
        RandomBot("Random2", 2),
        WildFirstBot("WildFirst1", 3),
        WildFirstBot("WildFirst2", 4),
        WildLastBot("WildLast1", 5),
        ZemtsevBot("Zemtsev", 6),
        WellBot("Helga", 7),
        AkimVBot("Akim", 8),
    ]

    tournament = UNOTournament(
        players=bots,
        games_per_match=15,  # Small for Swiss (multiple rounds)
        format=TournamentFormat.SWISS,
        seed=789,
    )

    winner = tournament.run_tournament()
    tournament.print_standings()
    tournament.print_tournament_stats()

    return tournament


def test_all_formats_small():
    """Test all formats with small number of players"""
    print("\n" + "=" * 70)
    print("TEST 5: All Formats Comparison (4 players)")
    print("=" * 70)

    bots = [
        RandomBot("Random", 1),
        WildFirstBot("WildFirst", 2),
        WildLastBot("WildLast", 3),
        ZemtsevBot("Zemtsev", 4),
    ]

    formats = [
        TournamentFormat.SINGLE_ELIMINATION,
        TournamentFormat.DOUBLE_ELIMINATION,
        TournamentFormat.ROUND_ROBIN,
        TournamentFormat.SWISS,
    ]

    format_names = {
        TournamentFormat.SINGLE_ELIMINATION: "Single Elimination",
        TournamentFormat.DOUBLE_ELIMINATION: "Double Elimination",
        TournamentFormat.ROUND_ROBIN: "Round Robin",
        TournamentFormat.SWISS: "Swiss System",
    }

    winners = {}

    for format in formats:
        print(f"\n{format_names[format]}:")
        print("-" * 40)

        tournament = UNOTournament(
            players=bots,
            games_per_match=10,  # Very small for quick comparison
            format=format,
            seed=999,
        )

        winner = tournament.run_tournament()
        if winner:
            winners[format.value] = winner.name
            print(f"Winner: {winner.name}")

    print("\n" + "=" * 40)
    print("Format Comparison Results:")
    print("=" * 40)
    for format_name, winner_name in winners.items():
        print(f"{format_name.replace('_', ' ').title():<20}: {winner_name}")


def test_duel():
    """Test a simple 1v1 duel"""
    print("\n" + "=" * 70)
    print("TEST 6: Simple Duel (1v1 Match)")
    print("=" * 70)

    from uno.engine.tournament import MatchResult

    bot1 = RandomBot("RandomBot", 1)
    bot2 = WildFirstBot("WildFirstBot", 2)

    match = MatchResult(bot1, bot2, games_per_match=20)
    result = match.run_match()

    print(f"Match: {bot1.name} vs {bot2.name}")
    print(f"Result: {result['player1_wins']} - {result['player2_wins']}")
    print(f"Winner: {result['winner']}")
    print(f"Is Draw: {result['is_draw']}")

    return match


if __name__ == "__main__":
    print("UNO Tournament System - All Formats Test Suite")
    print("=" * 70)

    # Run tests
    test_single_elimination()
    test_double_elimination()
    test_round_robin()
    test_swiss()
    test_all_formats_small()
    test_duel()

    print("\n" + "=" * 70)
    print("All tournament format tests completed successfully!")
    print("=" * 70)
