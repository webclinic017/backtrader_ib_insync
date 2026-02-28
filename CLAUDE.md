# CLAUDE.md

## Project Overview

`backtrader_ib_insync` is a Python library that integrates Interactive Brokers (IB) with the [Backtrader](https://www.backtrader.com/) algorithmic trading framework, using the modern `ib_insync` async API. It provides a live trading data feed, broker interface, and data store for connecting Backtrader strategies directly to IB TWS or IB Gateway.

## Project Structure

```
backtrader_ib_insync/
├── backtrader_ib_insync/
│   ├── __init__.py      # Package exports: IBStore, IBBroker, IBData
│   ├── ibstore.py       # IBStore — singleton IB connection & data/order coordination
│   ├── ibbroker.py      # IBBroker — Backtrader broker interface + IBOrder/IBCommInfo
│   └── ibdata.py        # IBData — data feed (real-time bars, RTVolume, historical)
├── examples/
│   └── ibdemo.py        # Demo strategy using EUR.USD historical data
├── requirements.txt     # ib_insync
└── setup.py             # Package metadata (version 0.0.1, Python >=3.6)
```

## Key Components

### IBStore (`ibstore.py`)
- **Singleton** — one IB connection per process
- Wraps `ib_insync.IB`; manages connection, reconnection, and time sync
- Handles historical data requests (with smart duration/bar-size splitting), real-time bar subscriptions, market data ticks, order placement/cancellation, and account updates
- Default ports: `7496` (live TWS), `7497` (paper trading)

### IBBroker (`ibbroker.py`)
- Implements Backtrader's `BrokerBase`
- Maps Backtrader order types to IB order types: `MKT`, `LMT`, `STP`, `STPLMT`, `TRAIL`, `TRAIL LIMIT`, `MOC`
- Supports TIF (`GTC`, `DAY`, `GTD`), trailing stops (amount or %), and OCA groups
- Tracks order status: `SUBMITTED`, `FILLED`, `CANCELLED`, `INACTIVE`, `PENDINGSUBMIT`, `PENDINGCANCEL`, `PRESUBMITTED`

### IBData (`ibdata.py`)
- Implements Backtrader's `DataBase`
- Supports real-time 5-second bars (`rtbar=True`) and RTVolume ticks
- Handles historical backfilling and optional alternative backfill source
- Contract specified via `dataname` string:
  - Stock: `TICKER` or `TICKER-STK-EXCHANGE-CURRENCY`
  - Forex: `CUR1.CUR2-CASH-IDEALPRO`
  - Futures: `TICKER-YYYYMM-EXCHANGE-CURRENCY-MULT`
  - Options: `TICKER-YYYYMMDD-EXCHANGE-CURRENCY-STRIKE-RIGHT-MULT`

## Installation

```bash
pip install git+https://github.com/ultra1971/backtrader_ib_insync
```

Or for local development:

```bash
pip install ib_insync backtrader
pip install -e .
```

## Running the Example

Requires IB TWS or IB Gateway running locally:

```bash
python examples/ibdemo.py
```

Edit `ibdemo.py` to set your `host`, `port`, `clientId`, and `account` as needed.

## Usage Pattern

```python
import backtrader as bt
import backtrader_ib_insync as ibnew

storekwargs = dict(
    host='127.0.0.1',
    port=7497,          # 7497 = paper, 7496 = live
    clientId=None,      # auto-generated if None
    reconnect=3,
    timeout=3.0,
)

store = ibnew.IBStore(**storekwargs)

data = store.getdata(
    dataname='AAPL-STK-SMART-USD',
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    historical=False,
    backfill_start=True,
)

cerebro = bt.Cerebro()
cerebro.setbroker(store.getbroker())
cerebro.adddata(data)
cerebro.addstrategy(MyStrategy)
cerebro.run()
```

## Development Notes

- **Python version:** 3.6+
- **License:** GNU General Public License v3
- **Status:** Alpha — functional but not production-hardened
- There are no automated tests in the repository; testing requires a live or paper IB connection
- `ib_insync` uses `asyncio`; ensure event loop compatibility when integrating with other async code
- The `IBStore` singleton means only one IB connection exists per Python process; use unique `clientId` values when running multiple processes against the same TWS/Gateway instance
