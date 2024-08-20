# TA Strategies and Algorithms on STOXX Europe 600 Equities

<br/>

This repository includes all research done to identify buy/sell signals on STOXX Europe 600 equities using technical analysis strategies, which is the focus of BBSP. All indicators are directly sourced from the [TA Library](https://technical-analysis-library-in-python.readthedocs.io/en/latest/).

The main algorithms/models are contained in the `divergences.py` and `momentum.py` files, identifying RSI-price divergences graphically and crossovers with combined moving averages respectively.

Some **other useful tools** in the repository include:

- Extrema detection algorithm for close prices using SKLearn
- Algorithm to identify perceptually important points and slopes in a stock's chart
- Some work on matrix profiles for pattern recognition using the [STUMPY](https://stumpy.readthedocs.io/en/latest/) library

<br/>

**Although the algorithms and approach are correct within the technical analysis framework, these strategies yield no significant results during backtesting.**
