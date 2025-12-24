import time
from typing import Dict, List

import matplotlib.pyplot as plt

from .engine import UnoGameEngine


class UnoSimulation:
    """
    Runs multiple UNO games and collects statistics.
    """

    def __init__(
        self, players: List, num_games: int = 1_000, endless_reshuffle: bool = True
    ):
        self.players = players
        self.num_games = num_games
        self.endless_reshuffle = endless_reshuffle
        self.win_counts = {player.name: 0 for player in players}
        self.turn_counts = []
        self.player_types = {player.name: type(player).__name__ for player in players}

    def run_simulation(self) -> Dict:
        """
        Run the simulation for the specified number of games.
        """

        start_time = time.time()

        for game_num in range(1, self.num_games + 1):
            # Create new game engine for each game
            game = UnoGameEngine(
                auto_play=True, turn_delay=0, endless_reshuffle=self.endless_reshuffle
            )

            # Add players (create new instances to reset state)
            for player in self.players:
                # Create new instance of the same bot type
                bot_class = type(player)
                new_player = bot_class(player.name, player.player_id)
                game.add_player(new_player)

            # Run the game
            try:
                winner = game.auto_play_game()
                if winner:
                    self.win_counts[winner.name] += 1
                    self.turn_counts.append(game.turn_count)
            except Exception as e:
                continue

        end_time = time.time()
        self.simulation_time = end_time - start_time

        return self._generate_statistics()

    def _generate_statistics(self) -> Dict:
        """
        Generate comprehensive statistics from the simulation.
        """
        total_wins = sum(self.win_counts.values())

        stats = {
            "total_games": self.num_games,
            "win_counts": self.win_counts,
            "win_percentages": {
                name: (count / total_wins * 100)
                for name, count in self.win_counts.items()
            },
            "average_turns": sum(self.turn_counts) / len(self.turn_counts)
            if self.turn_counts
            else 0,
            "simulation_time": self.simulation_time,
            "games_per_second": self.num_games / self.simulation_time
            if self.simulation_time > 0
            else 0,
            "player_types": self.player_types,
        }

        return stats

    def print_statistics(self, stats: Dict):
        """
        Print simulation statistics.
        """

        # Sort by win percentage
        sorted_wins = sorted(
            stats["win_counts"].items(), key=lambda x: x[1], reverse=True
        )

        for player_name, wins in sorted_wins:
            percentage = stats["win_percentages"][player_name]
            player_type = stats["player_types"][player_name]
            print(
                f"{player_name} ({player_type}): {wins:>5} wins ({percentage:>6.2f}%)"
            )

    def plot_statistics(self, stats: Dict):
        """
        Create matplotlib plots for the simulation results.
        """
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(
            f"UNO Bot Performance Analysis ({self.num_games:,} Games)",
            fontsize=16,
            fontweight="bold",
        )

        # Prepare data
        players = list(stats["win_counts"].keys())
        wins = list(stats["win_counts"].values())
        percentages = list(stats["win_percentages"].values())
        player_types = [stats["player_types"][player] for player in players]

        # Generate colors using matplotlib colormap for any number of bot types
        # Get unique bot types and assign colors from a colormap
        unique_types = list(set(player_types))
        colormap = plt.get_cmap("tab20")  # Good for categorical data
        type_colors = {}

        for i, bot_type in enumerate(unique_types):
            # Distribute colors evenly across the colormap range [0, 1]
            # Handle case when there's only one type
            if len(unique_types) == 1:
                type_colors[bot_type] = colormap(0.5)  # Use middle of colormap
            else:
                type_colors[bot_type] = colormap(i / (len(unique_types) - 1))

        colors = [type_colors[ptype] for ptype in player_types]

        # Plot 1: Win Count Bar Chart
        bars = ax1.bar(players, wins, color=colors, alpha=0.7, edgecolor="black")
        ax1.set_title("Total Wins by Bot", fontweight="bold")
        ax1.set_ylabel("Number of Wins")
        ax1.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
            )

        # Plot 2: Win Percentage Pie Chart
        ax2.pie(
            percentages, labels=players, autopct="%1.1f%%", startangle=90, colors=colors
        )
        ax2.set_title("Win Percentage Distribution", fontweight="bold")

        # Plot 3: Bot Type Performance
        type_performance = {}
        for player, wins in stats["win_counts"].items():
            ptype = stats["player_types"][player]
            if ptype not in type_performance:
                type_performance[ptype] = 0
            type_performance[ptype] += wins

        type_names = list(type_performance.keys())
        type_wins = list(type_performance.values())
        type_colors_plot = [type_colors[t] for t in type_names]

        ax3.bar(
            type_names, type_wins, color=type_colors_plot, alpha=0.7, edgecolor="black"
        )
        ax3.set_title("Performance by Bot Type", fontweight="bold")
        ax3.set_ylabel("Total Wins")
        ax3.tick_params(axis="x", rotation=45)

        # Plot 4: Turn Distribution Histogram
        if self.turn_counts:
            ax4.hist(
                self.turn_counts, bins=50, alpha=0.7, edgecolor="black", color="skyblue"
            )
            ax4.set_title("Game Length Distribution", fontweight="bold")
            ax4.set_xlabel("Number of Turns")
            ax4.set_ylabel("Frequency")
            ax4.axvline(
                stats["average_turns"],
                color="red",
                linestyle="--",
                label=f"Average: {stats['average_turns']:.1f} turns",
            )
            ax4.legend()

        plt.tight_layout()
        plt.savefig("uno_simulation_results.png", dpi=300, bbox_inches="tight")
        plt.show()
