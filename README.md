# UNO Engine & Bot Framework

A comprehensive UNO card game engine with multiple AI bot implementations, designed for simulating and analyzing UNO gameplay strategies at scale.

## Available Bot Types

| Bot Type | Strategy Description | Play Style |
|----------|---------------------|------------|
| **RandomBot** | Completely random valid moves | Chaotic |
| **WildFirstBot** | Plays wild cards immediately | Aggressive |
| **WildLastBot** | Saves wild cards for endgame | Conservative |
| **ZemtsevBot** | [Zemtsev Dmitriy](https://github.com/ByySpeenyx) |  |
| **KintselBot** | [Nikita Kintsel](https://github.com/nstathams) |  |
| **WellBot** | [Olga Usanova](https://github.com/WellHelga) |  |
| **AkimVBot** | [Volgin Akim](https://github.com/ggvp989) |  |
| **ZhadnovBot** | [Zhadnov Ivan](https://github.com/Vansoooo) |  |
| **SkripkinBot** | [Mikhail Skripkin](https://github.com/davbych) |  |


## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

#### uv 

[uv](https://docs.astral.sh/uv/) - an extremely fast Python package and project manager.

```bash
# Clone the repository
git clone <your-repo-url>
cd uno-engine-py

# Install dependencies
uv sync

# Install development dependencies
uv sync --dev
```

#### pip

[pip](https://pip.pypa.io/en/stable/installation/) 

```bash
python -m venv .venv

# Linux 
source .venv/bin/activate

# Windwos
.venv/bin/activate.bat

# Install dependencies
pip install -r requirements.txt
```


### Running Simulations

```bash
# Run the main simulation interface
uv run main.py
```

```
python3 main.py
```

or 

```
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
```

## Usage Examples


### Simulation
```python
from uno.simulation.runner import UnoSimulation
from uno.bots import *

bots = [
    RandomBot("Random1", 1),
    OffensiveBot("Offensive", 2),
    DefensiveBot("Defensive", 3),
    BalancedBot("Balanced", 4)
]

simulation = UnoSimulation(bots, num_games=10000)
stats = simulation.run_simulation()
simulation.plot_statistics(stats)
```


Example output from 10,000 game simulation:
```
Win Statistics:
----------------------------------------
WildFirst (WildFirstBot):  3357 wins ( 33.57%)
WildLast (WildLastBot):  1872 wins ( 18.72%)
Random4 (RandomBot):  1225 wins ( 12.25%)
Random2 (RandomBot):  1223 wins ( 12.23%)
Random1 (RandomBot):  1188 wins ( 11.88%)
Random3 (RandomBot):  1135 wins ( 11.35%)
```


![](images/uno_simulation_results.png)


## Creating New Bots

1. Extend the `Player` base class:
```python
from uno.player.player import Player

class MyCustomBot(Player):
    def choose_action(self) -> PlayerAction:
        """
        Choose which action to take
        Must be implemented by subclasses
        """
        pass
    def choose_color(self, wild_card: Card) -> CardColor:
        """
        Choose a color when playing a wild card
        Must be implemented by subclasses
        """
        pass
    def decide_say_uno(self) -> bool:
        """
        Decide whether to say UNO when down to one card
        Must be implemented by subclasses
        """
        pass
```


