"""
UNO Tournament System with Playoff Bracket
"""

import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .simulator import UnoSimulation


class TournamentFormat(Enum):
    """Tournament format options"""

    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"


class MatchResult:
    """Result of a single match between two players"""

    def __init__(self, player1: Any, player2: Any, games_per_match: int = 100):
        self.player1 = player1
        self.player2 = player2
        self.games_per_match = games_per_match
        self.player1_wins = 0
        self.player2_wins = 0
        self.draws = 0
        self.match_winner = None
        self.stats = None

    def run_match(self) -> Dict:
        """Run the match and return results"""
        simulation = UnoSimulation(
            players=[self.player1, self.player2],
            num_games=self.games_per_match,
            endless_reshuffle=True,
        )

        self.stats = simulation.run_simulation()

        # Determine winner based on win counts
        player1_wins = self.stats["win_counts"].get(self.player1.name, 0)
        player2_wins = self.stats["win_counts"].get(self.player2.name, 0)

        self.player1_wins = player1_wins
        self.player2_wins = player2_wins

        if player1_wins > player2_wins:
            self.match_winner = self.player1
        elif player2_wins > player1_wins:
            self.match_winner = self.player2
        else:
            # Draw - choose randomly
            self.match_winner = random.choice([self.player1, self.player2])
            self.draws = 1

        return {
            "player1": self.player1.name,
            "player2": self.player2.name,
            "player1_wins": player1_wins,
            "player2_wins": player2_wins,
            "winner": self.match_winner.name if self.match_winner else None,
            "is_draw": player1_wins == player2_wins,
            "stats": self.stats,
        }

    def __str__(self) -> str:
        if self.match_winner:
            return f"{self.player1.name} vs {self.player2.name}: {self.match_winner.name} wins ({self.player1_wins}-{self.player2_wins})"
        return f"{self.player1.name} vs {self.player2.name}: Not played"


@dataclass
class TournamentPlayer:
    """Player in a tournament with tracking"""

    bot: Any
    wins: int = 0
    losses: int = 0
    draws: int = 0
    points: int = 0
    eliminated: bool = False

    # For Swiss system
    opponents_faced: List[str] = None  # type: ignore
    swiss_score: float = 0.0
    buchholz_score: float = 0.0  # Tiebreaker: sum of opponents' scores

    def __post_init__(self):
        if self.opponents_faced is None:
            self.opponents_faced = []

    @property
    def name(self) -> str:
        return self.bot.name

    @property
    def bot_type(self) -> str:
        return type(self.bot).__name__

    @property
    def match_score(self) -> float:
        """Calculate match score for Swiss system (1 for win, 0.5 for draw, 0 for loss)"""
        return self.wins + (self.draws * 0.5)

    def add_opponent(self, opponent_name: str) -> None:
        """Add opponent to faced list for Swiss system"""
        if opponent_name not in self.opponents_faced:
            self.opponents_faced.append(opponent_name)


class TournamentRound:
    """A single round in the tournament"""

    def __init__(self, round_number: int, matches: List[MatchResult]):
        self.round_number = round_number
        self.matches = matches
        self.completed = False

    def run_round(self) -> List[TournamentPlayer]:
        """Run all matches in this round"""
        winners = []
        for match in self.matches:
            match.run_match()
            if match.match_winner:
                winners.append(match.match_winner)

        self.completed = True
        return winners

    def get_results(self) -> List[Dict]:
        """Get results of all matches in this round"""
        return [match.run_match() for match in self.matches]

    def __str__(self) -> str:
        matches_str = "\n  ".join(str(match) for match in self.matches)
        return f"Round {self.round_number}:\n  {matches_str}"


class UNOTournament:
    """
    UNO Tournament System with Playoff Bracket

    Features:
    - Single elimination bracket
    - Configurable number of games per match
    - Support for any bot types
    - Detailed statistics and results
    """

    def __init__(
        self,
        players: List,
        games_per_match: int = 100,
        format: TournamentFormat = TournamentFormat.SINGLE_ELIMINATION,
        seed: Optional[int] = None,
    ):
        """
        Initialize tournament

        Args:
            players: List of bot instances
            games_per_match: Number of UNO games per match
            format: Tournament format
            seed: Random seed for bracket generation
        """
        if len(players) < 2:
            raise ValueError("Tournament needs at least 2 players")

        self.original_players = players
        self.games_per_match = games_per_match
        self.format = format
        self.seed = seed

        if seed is not None:
            random.seed(seed)

        # Initialize tournament players
        self.players = [TournamentPlayer(bot) for bot in players]

        # Tournament state
        self.rounds: List[TournamentRound] = []
        self.current_round = 0
        self.winner: Optional[TournamentPlayer] = None
        self.completed = False
        self.results: List[Dict] = []
        self._match_players: List[Tuple[TournamentPlayer, TournamentPlayer]] = []
        self._next_round_players: List[TournamentPlayer] = []

        # Format-specific state
        self.is_double_elimination = False
        self.is_round_robin = False
        self.is_swiss = False
        self.winners_bracket: List[TournamentPlayer] = []
        self.losers_bracket: List[TournamentPlayer] = []
        self.final_round_players: List[TournamentPlayer] = []
        self.round_robin_matches: List[Tuple[TournamentPlayer, TournamentPlayer]] = []
        self.swiss_rounds: List[List[Tuple[TournamentPlayer, TournamentPlayer]]] = []
        self.swiss_pairings: List[Tuple[TournamentPlayer, TournamentPlayer]] = []

        # Initialize bracket
        self.create_bracket()

        # Statistics
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def create_bracket(self) -> None:
        """Create tournament bracket based on format"""
        if self.format == TournamentFormat.SINGLE_ELIMINATION:
            self._create_single_elimination_bracket()
        elif self.format == TournamentFormat.DOUBLE_ELIMINATION:
            self._create_double_elimination_bracket()
        elif self.format == TournamentFormat.ROUND_ROBIN:
            self._create_round_robin_bracket()
        elif self.format == TournamentFormat.SWISS:
            self._create_swiss_bracket()
        else:
            raise ValueError(f"Unknown tournament format: {self.format}")

    def _create_single_elimination_bracket(self) -> None:
        """Create single elimination bracket"""
        # Shuffle players for random seeding
        active_players = self.players.copy()
        random.shuffle(active_players)

        # Ensure number of players is power of 2 by adding byes if needed
        next_power_of_two = 1
        while next_power_of_two < len(active_players):
            next_power_of_two <<= 1

        # Add dummy players for byes
        byes_needed = next_power_of_two - len(active_players)
        for i in range(byes_needed):
            # Create a dummy player that will get a bye
            from ..bots import RandomBot

            dummy = RandomBot(f"BYE_{i}", 999 + i)
            active_players.append(TournamentPlayer(dummy))

        self.bracket = active_players
        self._generate_rounds(active_players)

    def _create_double_elimination_bracket(self) -> None:
        """Create double elimination bracket"""
        # For double elimination, we need winners bracket and losers bracket
        active_players = self.players.copy()
        random.shuffle(active_players)

        # Ensure number of players is power of 2
        next_power_of_two = 1
        while next_power_of_two < len(active_players):
            next_power_of_two <<= 1

        # Add BYEs if needed
        byes_needed = next_power_of_two - len(active_players)
        for i in range(byes_needed):
            from ..bots import RandomBot

            dummy = RandomBot(f"BYE_{i}", 999 + i)
            active_players.append(TournamentPlayer(dummy))

        self.bracket = active_players
        self.winners_bracket = active_players.copy()
        self.losers_bracket = []
        self.final_round_players = []

        # Mark as double elimination
        self.is_double_elimination = True

    def _create_round_robin_bracket(self) -> None:
        """Create round robin bracket - everyone plays everyone"""
        active_players = self.players.copy()
        random.shuffle(active_players)

        self.bracket = active_players
        self.round_robin_matches = []

        # Generate all possible pairings
        n = len(active_players)
        for i in range(n):
            for j in range(i + 1, n):
                self.round_robin_matches.append((active_players[i], active_players[j]))

        # Mark as round robin
        self.is_round_robin = True

    def _create_swiss_bracket(self) -> None:
        """Create Swiss system bracket"""
        active_players = self.players.copy()
        random.shuffle(active_players)

        self.bracket = active_players
        self.swiss_rounds = []
        self.swiss_pairings = []

        # For Swiss, we need to track opponents faced
        for player in active_players:
            player.opponents_faced = []
            player.swiss_score = 0

        # Mark as Swiss
        self.is_swiss = True

    def _generate_rounds(self, players: List[TournamentPlayer]) -> None:
        """Generate rounds for the bracket"""
        # This creates the bracket structure, but actual match pairing
        # and winner advancement happens when rounds are run
        self.bracket_players = players
        self._create_initial_matches()

    def _create_initial_matches(self) -> None:
        """Create first round matches from bracket players"""
        matches = []
        round_players = []

        # Pair players for first round
        for i in range(0, len(self.bracket_players), 2):
            if i + 1 < len(self.bracket_players):
                player1_t = self.bracket_players[i]
                player2_t = self.bracket_players[i + 1]

                # Skip matches where one player is a BYE
                if "BYE_" in player1_t.name or "BYE_" in player2_t.name:
                    # BYE automatically advances the real player
                    if "BYE_" in player1_t.name:
                        winner_t = player2_t
                        loser_t = player1_t
                    else:
                        winner_t = player1_t
                        loser_t = player2_t

                    winner_t.wins += 1
                    winner_t.points += 3
                    loser_t.losses += 1
                    loser_t.eliminated = True

                    # Winner advances to next round
                    round_players.append(winner_t)
                    continue

                match = MatchResult(player1_t.bot, player2_t.bot, self.games_per_match)
                matches.append(match)
                # Store which tournament players are in this match
                self._match_players.append((player1_t, player2_t))

        if matches:
            round_obj = TournamentRound(1, matches)
            self.rounds.append(round_obj)
            self._next_round_players = round_players  # Players with BYEs that advance

    def _create_next_round(
        self, round_number: int, winners: List[TournamentPlayer]
    ) -> None:
        """Create next round from winners of previous round"""
        if len(winners) <= 1:
            return  # Tournament finished

        matches = []
        self._match_players = []  # Reset for new round

        # Pair winners for next round
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                player1_t = winners[i]
                player2_t = winners[i + 1]
                match = MatchResult(player1_t.bot, player2_t.bot, self.games_per_match)
                matches.append(match)
                self._match_players.append((player1_t, player2_t))

        if matches:
            round_obj = TournamentRound(round_number, matches)
            self.rounds.append(round_obj)

    def _run_single_elimination(self) -> Optional[TournamentPlayer]:
        """Run single elimination tournament"""
        # Use existing single elimination logic
        round_number = 1
        current_winners = (
            self._next_round_players.copy()
            if hasattr(self, "_next_round_players")
            else []
        )

        while True:
            if round_number - 1 < len(self.rounds):
                round_obj = self.rounds[round_number - 1]
            else:
                break

            print(f"\nRound {round_number}:")
            print("-" * 30)

            round_winners = []
            match_index = 0

            for match in round_obj.matches:
                if match_index < len(self._match_players):
                    player1_t, player2_t = self._match_players[match_index]

                    match.run_match()

                    if match.match_winner == match.player1:
                        player1_t.wins += 1
                        player1_t.points += 3
                        player2_t.losses += 1
                        player2_t.eliminated = True
                        round_winners.append(player1_t)
                    elif match.match_winner == match.player2:
                        player2_t.wins += 1
                        player2_t.points += 3
                        player1_t.losses += 1
                        player1_t.eliminated = True
                        round_winners.append(player2_t)
                    else:
                        player1_t.draws += 1
                        player2_t.draws += 1
                        player1_t.points += 1
                        player2_t.points += 1
                        if random.random() < 0.5:
                            player1_t.wins += 1
                            player2_t.losses += 1
                            round_winners.append(player1_t)
                        else:
                            player2_t.wins += 1
                            player1_t.losses += 1
                            round_winners.append(player2_t)

                    self.results.append(
                        {
                            "round": round_number,
                            "player1": match.player1.name,
                            "player2": match.player2.name,
                            "player1_wins": match.player1_wins,
                            "player2_wins": match.player2_wins,
                            "winner": match.match_winner.name
                            if match.match_winner
                            else None,
                            "is_draw": match.player1_wins == match.player2_wins,
                        }
                    )

                    print(f"  {match}")
                    match_index += 1

            all_winners = current_winners + round_winners

            if len(all_winners) > 1:
                self._create_next_round(round_number + 1, all_winners)
                current_winners = []
            else:
                if all_winners:
                    return all_winners[0]
                break

            round_number += 1

        if current_winners and len(current_winners) == 1:
            return current_winners[0]

        return None

    def _run_double_elimination(self) -> Optional[TournamentPlayer]:
        """Run double elimination tournament"""
        print("\nDouble Elimination Tournament")
        print("=" * 30)

        # Winners bracket first round
        print("\nWinners Bracket - Round 1:")
        print("-" * 30)

        winners_bracket_matches = []
        winners_next_round = []
        losers_first_round = []

        # Pair players in winners bracket
        for i in range(0, len(self.winners_bracket), 2):
            if i + 1 < len(self.winners_bracket):
                player1_t = self.winners_bracket[i]
                player2_t = self.winners_bracket[i + 1]

                # Skip BYEs
                if "BYE_" in player1_t.name or "BYE_" in player2_t.name:
                    if "BYE_" in player1_t.name:
                        winner_t = player2_t
                        loser_t = player1_t
                    else:
                        winner_t = player1_t
                        loser_t = player2_t

                    winner_t.wins += 1
                    winner_t.points += 3
                    loser_t.losses += 1
                    losers_first_round.append(loser_t)
                    winners_next_round.append(winner_t)
                    continue

                match = MatchResult(player1_t.bot, player2_t.bot, self.games_per_match)
                match.run_match()

                if match.match_winner == match.player1:
                    player1_t.wins += 1
                    player1_t.points += 3
                    player2_t.losses += 1
                    winners_next_round.append(player1_t)
                    losers_first_round.append(player2_t)
                else:
                    player2_t.wins += 1
                    player2_t.points += 3
                    player1_t.losses += 1
                    winners_next_round.append(player2_t)
                    losers_first_round.append(player1_t)

                self.results.append(
                    {
                        "round": 1,
                        "bracket": "winners",
                        "player1": match.player1.name,
                        "player2": match.player2.name,
                        "player1_wins": match.player1_wins,
                        "player2_wins": match.player2_wins,
                        "winner": match.match_winner.name
                        if match.match_winner
                        else None,
                    }
                )

                print(f"  {match}")

        # Losers bracket first round
        self.losers_bracket = losers_first_round

        # Continue tournament until we have a winner
        round_num = 2
        while len(winners_next_round) > 1 or len(self.losers_bracket) > 1:
            # Winners bracket next round
            if len(winners_next_round) > 1:
                print(f"\nWinners Bracket - Round {round_num}:")
                print("-" * 30)

                new_winners = []
                new_losers = []

                for i in range(0, len(winners_next_round), 2):
                    if i + 1 < len(winners_next_round):
                        player1_t = winners_next_round[i]
                        player2_t = winners_next_round[i + 1]

                        match = MatchResult(
                            player1_t.bot, player2_t.bot, self.games_per_match
                        )
                        match.run_match()

                        if match.match_winner == match.player1:
                            player1_t.wins += 1
                            player1_t.points += 3
                            player2_t.losses += 1
                            new_winners.append(player1_t)
                            new_losers.append(player2_t)
                        else:
                            player2_t.wins += 1
                            player2_t.points += 3
                            player1_t.losses += 1
                            new_winners.append(player2_t)
                            new_losers.append(player1_t)

                        self.results.append(
                            {
                                "round": round_num,
                                "bracket": "winners",
                                "player1": match.player1.name,
                                "player2": match.player2.name,
                                "player1_wins": match.player1_wins,
                                "player2_wins": match.player2_wins,
                                "winner": match.match_winner.name
                                if match.match_winner
                                else None,
                            }
                        )

                        print(f"  {match}")

                winners_next_round = new_winners
                self.losers_bracket.extend(new_losers)

            # Losers bracket matches
            if len(self.losers_bracket) > 1:
                print(f"\nLosers Bracket - Round {round_num}:")
                print("-" * 30)

                losers_next_round = []

                for i in range(0, len(self.losers_bracket), 2):
                    if i + 1 < len(self.losers_bracket):
                        player1_t = self.losers_bracket[i]
                        player2_t = self.losers_bracket[i + 1]

                        match = MatchResult(
                            player1_t.bot, player2_t.bot, self.games_per_match
                        )
                        match.run_match()

                        if match.match_winner == match.player1:
                            player1_t.wins += 1
                            player1_t.points += 3
                            player2_t.losses += 1
                            player2_t.eliminated = True
                            losers_next_round.append(player1_t)
                        else:
                            player2_t.wins += 1
                            player2_t.points += 3
                            player1_t.losses += 1
                            player1_t.eliminated = True
                            losers_next_round.append(player2_t)

                        self.results.append(
                            {
                                "round": round_num,
                                "bracket": "losers",
                                "player1": match.player1.name,
                                "player2": match.player2.name,
                                "player1_wins": match.player1_wins,
                                "player2_wins": match.player2_wins,
                                "winner": match.match_winner.name
                                if match.match_winner
                                else None,
                            }
                        )

                        print(f"  {match}")

                self.losers_bracket = losers_next_round

            round_num += 1

        # Final: winners bracket winner vs losers bracket winner
        if winners_next_round and self.losers_bracket:
            print("\nGrand Final:")
            print("-" * 30)

            winners_winner = winners_next_round[0]
            losers_winner = self.losers_bracket[0]

            match = MatchResult(
                winners_winner.bot, losers_winner.bot, self.games_per_match
            )
            match.run_match()

            if match.match_winner == match.player1:
                winners_winner.wins += 1
                winners_winner.points += 3
                losers_winner.losses += 1
                champion = winners_winner
            else:
                # If losers bracket winner wins, need a second match (true double elimination)
                losers_winner.wins += 1
                losers_winner.points += 3
                winners_winner.losses += 1

                print("\nGrand Final - Match 2 (if needed):")
                print("-" * 30)

                match2 = MatchResult(
                    winners_winner.bot, losers_winner.bot, self.games_per_match
                )
                match2.run_match()

                if match2.match_winner == match2.player1:
                    winners_winner.wins += 1
                    winners_winner.points += 3
                    losers_winner.losses += 1
                    champion = winners_winner
                else:
                    losers_winner.wins += 1
                    losers_winner.points += 3
                    winners_winner.losses += 1
                    champion = losers_winner

                print(f"  {match2}")

            self.results.append(
                {
                    "round": round_num,
                    "bracket": "final",
                    "player1": match.player1.name,
                    "player2": match.player2.name,
                    "player1_wins": match.player1_wins,
                    "player2_wins": match.player2_wins,
                    "winner": match.match_winner.name if match.match_winner else None,
                }
            )

            print(f"  {match}")
            return champion

        return None

    def _run_round_robin(self) -> Optional[TournamentPlayer]:
        """Run round robin tournament"""
        print("\nRound Robin Tournament")
        print("=" * 30)

        round_num = 1
        matches_per_round = len(self.players) // 2

        # Play all matches
        for i, (player1_t, player2_t) in enumerate(self.round_robin_matches):
            if i % matches_per_round == 0:
                print(f"\nRound {round_num}:")
                print("-" * 30)
                round_num += 1

            match = MatchResult(player1_t.bot, player2_t.bot, self.games_per_match)
            match.run_match()

            if match.match_winner == match.player1:
                player1_t.wins += 1
                player1_t.points += 3
                player2_t.losses += 1
            elif match.match_winner == match.player2:
                player2_t.wins += 1
                player2_t.points += 3
                player1_t.losses += 1
            else:
                player1_t.draws += 1
                player2_t.draws += 1
                player1_t.points += 1
                player2_t.points += 1

            self.results.append(
                {
                    "round": (i // matches_per_round) + 1,
                    "player1": match.player1.name,
                    "player2": match.player2.name,
                    "player1_wins": match.player1_wins,
                    "player2_wins": match.player2_wins,
                    "winner": match.match_winner.name if match.match_winner else None,
                    "is_draw": match.player1_wins == match.player2_wins,
                }
            )

            print(f"  {match}")

        # Determine winner by points
        standings = self.get_standings()
        if standings:
            return standings[0]

        return None

    def _run_swiss(self) -> Optional[TournamentPlayer]:
        """Run Swiss system tournament"""
        print("\nSwiss System Tournament")
        print("=" * 30)

        num_rounds = min(5, len(self.players))  # Typically 4-7 rounds for Swiss

        for round_num in range(1, num_rounds + 1):
            print(f"\nRound {round_num}:")
            print("-" * 30)

            # Sort players by Swiss score (wins + 0.5 * draws)
            sorted_players = sorted(
                self.players,
                key=lambda p: (p.match_score, random.random()),
                reverse=True,
            )

            # Pair players
            pairings = []
            paired_indices = set()

            for i, player1 in enumerate(sorted_players):
                if i in paired_indices:
                    continue

                # Find opponent with similar score not already faced
                for j in range(i + 1, len(sorted_players)):
                    if j in paired_indices:
                        continue

                    player2 = sorted_players[j]

                    # Check if players have already faced each other
                    if (
                        player2.name in player1.opponents_faced
                        or player1.name in player2.opponents_faced
                    ):
                        continue

                    # Good pairing found
                    pairings.append((player1, player2))
                    paired_indices.add(i)
                    paired_indices.add(j)
                    break

            # Play matches
            for player1_t, player2_t in pairings:
                match = MatchResult(player1_t.bot, player2_t.bot, self.games_per_match)
                match.run_match()

                # Update scores
                if match.match_winner == match.player1:
                    player1_t.wins += 1
                    player1_t.points += 3
                    player2_t.losses += 1
                elif match.match_winner == match.player2:
                    player2_t.wins += 1
                    player2_t.points += 3
                    player1_t.losses += 1
                else:
                    player1_t.draws += 1
                    player2_t.draws += 1
                    player1_t.points += 1
                    player2_t.points += 1

                # Record opponents
                player1_t.add_opponent(player2_t.name)
                player2_t.add_opponent(player1_t.name)

                self.results.append(
                    {
                        "round": round_num,
                        "player1": match.player1.name,
                        "player2": match.player2.name,
                        "player1_wins": match.player1_wins,
                        "player2_wins": match.player2_wins,
                        "winner": match.match_winner.name
                        if match.match_winner
                        else None,
                        "is_draw": match.player1_wins == match.player2_wins,
                    }
                )

                print(f"  {match}")

            self.swiss_rounds.append(pairings)

        # Calculate Buchholz scores (sum of opponents' scores)
        for player in self.players:
            player.buchholz_score = sum(
                opp.match_score
                for opp in self.players
                if opp.name in player.opponents_faced
            )

        # Determine winner by points, then Buchholz
        standings = sorted(
            self.players,
            key=lambda p: (p.points, p.buchholz_score, p.wins),
            reverse=True,
        )

        if standings:
            return standings[0]

        return None

    def run_tournament(self) -> Optional[TournamentPlayer]:
        """
        Run the entire tournament

        Returns:
            TournamentPlayer: The tournament winner, or None if tournament not completed
        """
        self.start_time = time.time()

        print(f"Starting UNO Tournament with {len(self.players)} players")
        print(f"Format: {self.format.value}")
        print(f"Games per match: {self.games_per_match}")
        print("-" * 50)

        # Run tournament based on format
        if self.format == TournamentFormat.SINGLE_ELIMINATION:
            self.winner = self._run_single_elimination()
        elif self.format == TournamentFormat.DOUBLE_ELIMINATION:
            self.winner = self._run_double_elimination()
        elif self.format == TournamentFormat.ROUND_ROBIN:
            self.winner = self._run_round_robin()
        elif self.format == TournamentFormat.SWISS:
            self.winner = self._run_swiss()
        else:
            raise ValueError(f"Unknown tournament format: {self.format}")

        self.end_time = time.time()
        self.completed = True

        print("\n" + "=" * 50)
        print("TOURNAMENT COMPLETE!")
        if self.winner:
            print(f"CHAMPION: {self.winner.name} ({self.winner.bot_type})")
        print("=" * 50)

        return self.winner

    def get_standings(self) -> List[TournamentPlayer]:
        """Get tournament standings sorted appropriately for format"""
        if self.format == TournamentFormat.SWISS:
            # Swiss: points, then Buchholz, then wins
            return sorted(
                self.players,
                key=lambda p: (p.points, p.buchholz_score, p.wins, -p.losses),
                reverse=True,
            )
        else:
            # Other formats: points, wins, losses
            return sorted(
                self.players, key=lambda p: (p.points, p.wins, -p.losses), reverse=True
            )

    def print_standings(self) -> None:
        """Print tournament standings"""
        standings = self.get_standings()

        if self.format == TournamentFormat.SWISS:
            print("\nSwiss Tournament Standings:")
            print("-" * 80)
            print(
                f"{'Rank':<5} {'Player':<20} {'W':<4} {'L':<4} {'D':<4} {'Pts':<6} {'Buchholz':<10} {'Type':<15}"
            )
            print("-" * 80)

            for i, player in enumerate(standings, 1):
                print(
                    f"{i:<5} {player.name:<20} {player.wins:<4} {player.losses:<4} "
                    f"{player.draws:<4} {player.points:<6} {player.buchholz_score:<10.1f} {player.bot_type:<15}"
                )
        else:
            print("\nTournament Standings:")
            print("-" * 60)
            print(
                f"{'Rank':<5} {'Player':<20} {'W':<4} {'L':<4} {'D':<4} {'Pts':<6} {'Type':<15}"
            )
            print("-" * 60)

            for i, player in enumerate(standings, 1):
                print(
                    f"{i:<5} {player.name:<20} {player.wins:<4} {player.losses:<4} "
                    f"{player.draws:<4} {player.points:<6} {player.bot_type:<15}"
                )

    def get_match_history(self, player_name: str) -> List[Dict]:
        """Get match history for a specific player"""
        return [
            result
            for result in self.results
            if result["player1"] == player_name or result["player2"] == player_name
        ]

    def get_tournament_stats(self) -> Dict:
        """Get overall tournament statistics"""
        if not self.completed:
            return {}

        total_matches = sum(len(round_obj.matches) for round_obj in self.rounds)
        total_games = total_matches * self.games_per_match

        return {
            "total_players": len(self.players),
            "total_rounds": len(self.rounds),
            "total_matches": total_matches,
            "total_games": total_games,
            "winner": self.winner.name if self.winner else None,
            "winner_bot_type": self.winner.bot_type if self.winner else None,
            "duration_seconds": self.end_time - self.start_time
            if self.end_time and self.start_time
            else 0,
            "format": self.format.value,
            "games_per_match": self.games_per_match,
        }

    def print_tournament_stats(self) -> None:
        """Print tournament statistics"""
        stats = self.get_tournament_stats()

        print("\nTournament Statistics:")
        print("-" * 40)
        for key, value in stats.items():
            if key == "duration_seconds":
                print(f"{key.replace('_', ' ').title():<20}: {value:.2f}s")
            else:
                print(f"{key.replace('_', ' ').title():<20}: {value}")


def run_example_tournament():
    """Run an example tournament with default bots"""
    from ..bots import (
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

    # Create bots for tournament
    bots = [
        RandomBot("Random1", 1),
        WildFirstBot("WildFirst1", 2),
        WildLastBot("WildLast1", 3),
        ZemtsevBot("Zemtsev", 4),
        WellBot("Helga", 5),
        AkimVBot("Akim", 6),
        ZhadnovBot("Zhadnov", 7),
        SkripkinBot("Skripkin", 8),
        KintselBot("Kintsel", 9),
    ]

    # Create and run tournament
    tournament = UNOTournament(
        players=bots,
        games_per_match=50,  # Fewer games for faster demo
        format=TournamentFormat.SINGLE_ELIMINATION,
        seed=42,
    )

    winner = tournament.run_tournament()
    tournament.print_standings()
    tournament.print_tournament_stats()

    return tournament


if __name__ == "__main__":
    run_example_tournament()
