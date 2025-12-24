#!/usr/bin/env python3
"""
UNO Simulation CLI Entry Point

This module provides both a command-line interface and programmatic API
for running UNO simulations with configurable parameters.
"""

import argparse
import sys
import json
from typing import List, Dict, Any
from pathlib import Path

from uno.engine import UnoSimulation

# Imports Bots
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


class UNOCLI:
    """Command-line interface for UNO simulations"""

    def __init__(self):
        self.parser = self._setup_parser()

    def _setup_parser(self) -> argparse.ArgumentParser:
        """Configure argument parser"""
        parser = argparse.ArgumentParser(
            description="UNO Game Simulation Engine",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run default comparison simulation
  python main.py
  
  # Run with custom number of games
  python main.py --games 5000
  
  # Run specific bot configuration
  python main.py --bots RandomBot WildFirstBot --names "Random Player" "Wild Strategy"
  
  # Save results to file
  python main.py --output results.json --format json
  
  # Run in quiet mode for batch processing
  python main.py --quiet --games 10000
            """,
        )

        # Simulation parameters
        sim_group = parser.add_argument_group("Simulation Parameters")
        sim_group.add_argument(
            "--games",
            "-g",
            type=int,
            default=1000,
            help="Number of games to simulate (default: 1000)",
        )
        sim_group.add_argument(
            "--no-reshuffle",
            action="store_false",
            dest="endless_reshuffle",
            default=True,
            help="Disable endless deck reshuffling (single shuffle at start)",
        )
        sim_group.add_argument(
            "--bots",
            "-b",
            nargs="+",
            choices=["RandomBot", "WildFirstBot", "WildLastBot"],
            default=["RandomBot", "WildFirstBot"],
            help="Bot types to include in simulation",
        )
        sim_group.add_argument(
            "--names",
            "-n",
            nargs="+",
            help="Custom names for bots (must match number of bots)",
        )
        sim_group.add_argument(
            "--seeds",
            "-s",
            nargs="+",
            type=int,
            help="Random seeds for bots (must match number of bots)",
        )

        # Output options
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "--output", "-o", type=str, help="Output file path for results"
        )
        output_group.add_argument(
            "--format",
            choices=["json", "csv"],
            default="json",
            help="Output format (default: json)",
        )
        output_group.add_argument(
            "--quiet", "-q", action="store_true", help="Suppress console output"
        )
        output_group.add_argument(
            "--no-plot", action="store_true", help="Disable visualization plots"
        )

        return parser

    def create_bots(self, args: argparse.Namespace) -> List:
        """Instantiate bot objects based on CLI arguments"""
        bot_classes = {
            "RandomBot": RandomBot,
            "WildFirstBot": WildFirstBot,
        }

        bots = []
        for i, bot_type in enumerate(args.bots):
            # Get bot class
            bot_class = bot_classes[bot_type]

            # Configure name
            name = (
                args.names[i]
                if args.names and i < len(args.names)
                else f"{bot_type}_{i + 1}"
            )

            # Configure seed
            seed = args.seeds[i] if args.seeds and i < len(args.seeds) else None

            # Instantiate bot
            if bot_class == RandomBot:
                bot = bot_class(name, seed or i + 1)
            else:  # WildFirstBot, WildLastBot
                bot = bot_class(name, seed or i + 1)

            bots.append(bot)

        return bots

    def save_results(self, stats: Dict[str, Any], args: argparse.Namespace) -> None:
        """Save simulation results to file"""
        if not args.output:
            return

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.format == "json":
            with open(output_path, "w") as f:
                json.dump(stats, f, indent=2)
        elif args.format == "csv":
            # Implement CSV export if needed
            pass

        if not args.quiet:
            print(f"Results saved to: {output_path}")

    def run(self, args=None) -> Dict[str, Any]:
        """Execute UNO simulation with given arguments"""
        if args is None:
            args = self.parser.parse_args()

        # Validate arguments
        if args.names and len(args.names) != len(args.bots):
            self.parser.error("Number of names must match number of bots")

        if args.seeds and len(args.seeds) != len(args.bots):
            self.parser.error("Number of seeds must match number of bots")

        # Create bots
        bots = self.create_bots(args)

        if not args.quiet:
            print("Starting UNO Simulation")
            print(f"Configuration: {len(bots)} bots, {args.games} games")
            for bot in bots:
                print(f"  - {bot.name} ({bot.__class__.__name__})")
            print("-" * 50)

        # Run simulation
        simulation = UnoSimulation(
            bots, num_games=args.games, endless_reshuffle=args.endless_reshuffle
        )
        stats = simulation.run_simulation()

        # Output results
        if not args.quiet:
            simulation.print_statistics(stats)

            if not args.no_plot:
                simulation.plot_statistics(stats)

        # Save results
        self.save_results(stats, args)

        return stats


def run_default_simulation() -> Dict[str, Any]:
    """
    Run default comparison simulation.

    Returns:
        Dictionary containing simulation statistics
    """
    bots = [
        ZemtsevBot("Zemtsev", 1),
        WellBot("Helga", 2),
        AkimVBot("Akim", 3),
        ZhadnovBot("Zhadnov", 4),
        SkripkinBot("Skripkin", 5),
        KintselBot("Kintsel", 6),
        RandomBot("Random", 7),
        WildFirstBot("FirstBot", 8),
        WildLastBot("LastBot", 9),
        RandomBot("Random", 10),
    ]

    simulation = UnoSimulation(bots, num_games=1_000, endless_reshuffle=False)
    stats = simulation.run_simulation()

    simulation.print_statistics(stats)
    simulation.plot_statistics(stats)

    return stats


def main():
    """Main entry point"""
    cli = UNOCLI()

    try:
        # If no arguments provided, run default simulation
        if len(sys.argv) == 1:
            print("Running default UNO simulation...")
            stats = run_default_simulation()
        else:
            stats = cli.run()

        sys.exit(0)

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during simulation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
