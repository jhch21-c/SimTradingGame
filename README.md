# SimTradingGame

A Python-based simulated trading platform with real-time price updates, strategy testing, and portfolio management.

## Features

- Real-time stock price charts and market data
- User authentication and portfolio management
- Custom trading strategy creation and testing
- Order placement and matching system
- Admin interface for system management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SimTradingGame.git
cd SimTradingGame
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run user_terminal/main.py
```

## Project Structure

```
SimTradingGame/
├── src/
│   ├── web/              # Web interface components
│   │   ├── pages/        # Streamlit pages
│   │   └── components/   # Reusable UI components
│   ├── core/             # Core trading functionality
│   │   ├── models/       # Data models
│   │   ├── database/     # Database managers
│   │   └── trading/      # Trading logic
│   └── strategies/       # Trading strategy implementations
├── tests/                # Test suite
├── data/                 # Database files and market data
└── docs/                # Documentation
```

## Usage

1. Register a new account or log in with existing credentials
2. View real-time market data and your portfolio in the Overview page
3. Create and test trading strategies in the Strategy page
4. Monitor and manage orders in real-time
5. Admin users can access additional system management features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

