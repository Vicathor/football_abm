# Football Agent-Based Model (ABM)

A sophisticated agent-based simulation of football (soccer) matches using intelligent agents for tactical analysis and process mining.

## 🏈 Features

- **Multi-Agent Simulation**: Individual player agents with different roles (Goalkeeper, Centre-Back, Midfielder, Striker)
- **Tactical Formations**: Support for 4-4-2 formation (extensible to other formations)
- **Event Logging**: Process mining compatible event logging for tactical analysis
- **Real-time Decision Making**: Agents make decisions based on game context, pressure, and tactical awareness
- **Performance Metrics**: Track passes, shots, possession, and expected goals (xG)

## 🏗️ Architecture

```
football_abm/
├── abm/
│   ├── agents/          # Player agent implementations
│   ├── environment/     # Pitch and ball physics
│   ├── logging/         # Event logging for process mining
│   └── simulation/      # Main simulation engine
├── tests/              # Unit tests
└── main.py            # Entry point
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- NumPy
- Pandas

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Vicathor/football_abm.git
cd football_abm
```

2. Install dependencies:
```bash
pip install numpy pandas
```

3. Run the simulation:
```bash
python main.py
```

## 📊 Output

The simulation generates:
- **Event logs** in CSV format for process mining analysis
- **Match statistics** (possession, passes, shots, goals)
- **Tactical insights** with spatial and temporal context

### Sample Output
```
🏈 Football Tactics Simulation Starting...
Final Score: Home 0 - 0 Away
Total Events Logged: 26,393
Unique Possessions: 2,400
```

## 🎯 Use Cases

- **Tactical Analysis**: Analyze team formations and player movements
- **Process Mining**: Study football processes using event logs
- **Strategy Testing**: Test different tactical approaches
- **Player Performance**: Evaluate individual agent decision-making
- **Research**: Academic research in sports analytics and multi-agent systems

## 🔧 Configuration

### Team Formations
Currently supports 4-4-2 formation. Extend by modifying `formations` dictionary in `FootballSimulation._create_team()`.

### Simulation Parameters
- **Match Duration**: Adjust in `main.py` (default: 2 minutes for testing)
- **Timestep**: 100ms per simulation step
- **Player Attributes**: Customize in agent classes

## 📈 Event Data Schema

The simulation logs events with the following attributes:
- `case_id`: Possession sequence identifier
- `activity`: Action type (pass, shot, dribble, etc.)
- `player_role`, `team`: Agent information
- `pitch_zone`, `sub_zone`: Spatial context
- `pressure_level`: Tactical pressure
- `xg_added`: Expected goal contribution

## 🛠️ Development

### Adding New Player Types
1. Inherit from `FootballAgent` in `abm/agents/base_agent.py`
2. Implement decision-making logic in `decide_action()`
3. Add to team creation in `football_simulation.py`

### Custom Formations
1. Add formation definition to `formations` dictionary
2. Define player positions and roles
3. Update team creation logic

## 📋 TODO

- [ ] Implement more formations (4-3-3, 3-5-2, etc.)
- [ ] Add goalkeeper-specific behaviors
- [ ] Implement XES export for PM4Py
- [ ] Add visualization capabilities
- [ ] Advanced player attributes and skills
- [ ] Set pieces (corners, free kicks)
- [ ] Injury and substitution mechanics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-formation`)
3. Commit changes (`git commit -am 'Add 4-3-3 formation'`)
4. Push to branch (`git push origin feature/new-formation`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎓 Academic Use

If you use this simulation in academic research, please cite:

```
Football Agent-Based Model for Tactical Analysis
Victor Cebotar, 2025
https://github.com/Vicathor/football_abm
```

## 📞 Contact

- GitHub: [@Vicathor](https://github.com/Vicathor)
- Project Link: [https://github.com/Vicathor/football_abm](https://github.com/Vicathor/football_abm)
