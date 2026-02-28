# backtrader_ib_insync

A Python library that integrates [Interactive Brokers](https://www.interactivebrokers.com/) with the [Backtrader](https://www.backtrader.com/) algorithmic trading framework using the modern [`ib_insync`](https://github.com/erdewit/ib_insync) async API.

**Status:** Alpha — functional but not production-hardened.

---

## Features

- Live and historical data feeds from IB TWS or IB Gateway
- Real-time 5-second bars and RTVolume tick data
- Automatic historical backfilling on startup or reconnection
- Full broker interface: place, cancel, and track orders
- Supported order types: Market, Limit, Stop, Stop-Limit, Trailing Stop, Trailing Stop-Limit, Market-on-Close
- TIF support: `DAY`, `GTC`, `GTD`
- Supports stocks, forex, futures, and options
- OCA (One-Cancels-All) group support
- Automatic reconnection with configurable retry logic
- Python 3.6+ compatible (including Python 3.14)

---

## Installation

### From GitHub

```bash
pip install git+https://github.com/ultra1971/backtrader_ib_insync
```

### For local development

```bash
git clone https://github.com/ultra1971/backtrader_ib_insync
cd backtrader_ib_insync
pip install ib_insync backtrader
pip install -e .
```

---

## Requirements

- Python 3.6+
- `ib_insync`
- `backtrader`
- IB TWS or IB Gateway running and configured to accept API connections

---

## Quick Start

```python
import backtrader as bt
import backtrader_ib_insync as ibnew

class MyStrategy(bt.Strategy):
    def next(self):
        if not self.position:
            self.buy(size=100)

store = ibnew.IBStore(
    host='127.0.0.1',
    port=7497,       # 7497 = paper trading, 7496 = live
    clientId=1,
)

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

---

## IBStore

`IBStore` is a **singleton** — only one IB connection exists per Python process. All `IBData` and `IBBroker` instances share it.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | `'127.0.0.1'` | IB TWS or Gateway hostname |
| `port` | `7496` | Port (`7496` = live TWS, `7497` = paper trading) |
| `clientId` | `None` | Client ID. If `None`, a random ID (1–65535) is generated |
| `reconnect` | `3` | Reconnection attempts. `-1` = forever, `0` = disabled, `>0` = N retries |
| `timeout` | `3.0` | Seconds between reconnection attempts |
| `timeoffset` | `True` | Sync bar timestamps with IB server time |
| `timerefresh` | `60.0` | Seconds between server time offset refreshes |
| `readonly` | `False` | Set to `True` for read-only API mode |
| `account` | `''` | Main account string for updates. Defaults to first managed account |
| `indcash` | `True` | Treat `IND` security type codes as `CASH` |
| `_debug` | `False` | Enable verbose debug logging |

### Usage

```python
import backtrader_ib_insync as ibnew

store = ibnew.IBStore(
    host='127.0.0.1',
    port=7497,
    clientId=1,
    reconnect=3,
    timeout=3.0,
)

# Get a data feed
data = store.getdata(dataname='AAPL-STK-SMART-USD', ...)

# Get a broker
broker = store.getbroker()
```

---

## IBData

`IBData` is a Backtrader `DataBase` implementation that retrieves live and historical data from IB.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dataname` | — | Contract identifier string (see formats below) |
| `sectype` | `'STK'` | Security type fallback if not in `dataname` |
| `exchange` | `'SMART'` | Exchange fallback if not in `dataname` |
| `currency` | `''` | Currency fallback if not in `dataname` |
| `rtbar` | `False` | Use real-time 5-second bars instead of tick data |
| `historical` | `False` | Fetch historical data only, then stop |
| `what` | `None` | Data type: `'TRADES'`, `'MIDPOINT'`, `'BID'`, `'ASK'`, `'BID_ASK'` |
| `useRTH` | `False` | Regular trading hours only |
| `qcheck` | `0.5` | Queue check interval in seconds |
| `backfill_start` | `True` | Backfill historical data when starting |
| `backfill` | `True` | Backfill after reconnection |
| `backfill_from` | `None` | Alternative `DataBase` source for backfilling |
| `latethrough` | `False` | Allow late ticks to pass through |
| `tradename` | `None` | Separate contract string to use for trading (different from data source) |
| `hist_tzo` | `0` | Timezone offset in hours for historical data timestamps |

### Dataname Format

The `dataname` string defines the IB contract. The general format is:

```
SYMBOL-SECTYPE-EXCHANGE-CURRENCY-EXTRA
```

Fields not provided fall back to the `sectype`, `exchange`, and `currency` parameters.

| Asset Type | Format | Example |
|------------|--------|---------|
| Stock (simple) | `TICKER` | `AAPL` |
| Stock (full) | `TICKER-STK-EXCHANGE-CURRENCY` | `AAPL-STK-SMART-USD` |
| Forex | `BASE.QUOTE-CASH-IDEALPRO` | `EUR.USD-CASH-IDEALPRO` |
| Future | `TICKER-YYYYMM-EXCHANGE-CURRENCY-MULT` | `ES-202412-CME-USD-50` |
| Option | `TICKER-YYYYMMDD-EXCHANGE-CURRENCY-STRIKE-RIGHT-MULT` | `AAPL-20241220-SMART-USD-200-C-100` |
| Index | `TICKER-IND-EXCHANGE-CURRENCY` | `SPX-IND-CBOE-USD` |

### Examples

```python
# Historical data only
data = store.getdata(
    dataname='AAPL-STK-SMART-USD',
    timeframe=bt.TimeFrame.Days,
    compression=1,
    historical=True,
    fromdate=datetime(2024, 1, 1),
    todate=datetime(2024, 12, 31),
)

# Live data with backfill
data = store.getdata(
    dataname='EUR.USD-CASH-IDEALPRO',
    timeframe=bt.TimeFrame.Minutes,
    compression=5,
    historical=False,
    backfill_start=True,
    rtbar=False,
)

# Real-time 5-second bars
data = store.getdata(
    dataname='ES-202412-CME-USD-50',
    timeframe=bt.TimeFrame.Seconds,
    compression=5,
    rtbar=True,
)
```

---

## IBBroker

`IBBroker` implements Backtrader's `BrokerBase` and routes orders to IB. Get an instance via `store.getbroker()`.

```python
broker = store.getbroker(account='U1234567')
cerebro.setbroker(broker)
```

### Order Types

Backtrader order types map to IB order types as follows:

| Backtrader Type | IB Type | Description |
|-----------------|---------|-------------|
| `Order.Market` | `MKT` | Market order |
| `Order.Limit` | `LMT` | Limit order |
| `Order.Close` | `MOC` | Market-on-Close |
| `Order.Stop` | `STP` | Stop order |
| `Order.StopLimit` | `STPLMT` | Stop-Limit order |
| `Order.StopTrail` | `TRAIL` | Trailing stop (amount or %) |
| `Order.StopTrailLimit` | `TRAIL LIMIT` | Trailing stop-limit |

### Placing Orders

Orders are placed through Backtrader's standard `buy()` and `sell()` methods:

```python
class MyStrategy(bt.Strategy):
    def next(self):
        # Market order
        self.buy(size=100)

        # Limit order
        self.buy(size=100, exectype=bt.Order.Limit, price=150.00)

        # Stop order
        self.sell(size=100, exectype=bt.Order.Stop, price=145.00)

        # Stop-Limit order
        self.sell(size=100, exectype=bt.Order.StopLimit,
                  price=145.00, plimit=144.50)

        # Trailing stop (fixed amount)
        self.sell(size=100, exectype=bt.Order.StopTrail, trailamount=2.0)

        # Trailing stop (percentage)
        self.sell(size=100, exectype=bt.Order.StopTrail, trailpercent=0.02)
```

### Time in Force

Pass `valid` to control TIF:

```python
from datetime import datetime, timedelta

# DAY order (expires end of session)
self.buy(size=100, valid=bt.Order.DAY)

# GTC (Good-Till-Cancelled)
self.buy(size=100, valid=bt.Order.GTC)

# GTD (Good-Till-Date)
expiry = datetime.now() + timedelta(days=5)
self.buy(size=100, valid=expiry)
```

### OCA Groups

To create a One-Cancels-All group, pass `oco` referencing another order:

```python
buy_order = self.buy(size=100, exectype=bt.Order.Limit, price=150.0)
stop_order = self.sell(size=100, exectype=bt.Order.Stop,
                       price=145.0, oco=buy_order)
```

---

## Full Example

```python
import backtrader as bt
import backtrader_ib_insync as ibnew
from datetime import datetime

class IBStrategy(bt.Strategy):
    params = (
        ('stake', 100),
    )

    def __init__(self):
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed:
            action = 'BUY' if order.isbuy() else 'SELL'
            print(f'{action} EXECUTED: price={order.executed.price:.2f}, '
                  f'size={order.executed.size}')
        self.order = None

    def next(self):
        if self.order:
            return
        if not self.position:
            self.order = self.buy(size=self.p.stake)
        else:
            self.order = self.sell(size=self.p.stake)


def run():
    store = ibnew.IBStore(
        host='127.0.0.1',
        port=7497,          # paper trading
        clientId=1,
        reconnect=3,
        timeout=3.0,
        _debug=False,
    )

    data = store.getdata(
        dataname='AAPL-STK-SMART-USD',
        timeframe=bt.TimeFrame.Minutes,
        compression=1,
        historical=True,
        fromdate=datetime(2024, 1, 1),
        todate=datetime(2024, 1, 31),
        backfill_start=False,
    )

    cerebro = bt.Cerebro()
    cerebro.setbroker(store.getbroker())
    cerebro.adddata(data)
    cerebro.addstrategy(IBStrategy, stake=100)
    cerebro.run()
    print(f'Final portfolio value: {cerebro.broker.getvalue():.2f}')


if __name__ == '__main__':
    run()
```

---

## IB TWS / Gateway Configuration

1. Open TWS or IB Gateway
2. Go to **Edit → Global Configuration → API → Settings**
3. Enable **Enable ActiveX and Socket Clients**
4. Set the **Socket port** (`7496` for live, `7497` for paper)
5. Add `127.0.0.1` to the **Trusted IP Addresses** list (or your remote host)
6. Optionally enable **Read-Only API** if you only need market data

---

## Python 3.14 Compatibility

Python 3.14 enforces that `asyncio.timeout()` must be used inside an `asyncio.Task`. This library wraps `ib_insync`'s `connectAsync()` inside `asyncio.ensure_future()` to satisfy this requirement. No special configuration is needed — it works out of the box on Python 3.14+.

---

## Architecture

```
cerebro.run()
    │
    ├── IBData._load()          ← pulls bars from Queue
    │       │
    │       └── IBStore         ← submits historical/RT data requests to IB
    │               │
    │               └── ib_insync.IB  ← async connection to TWS/Gateway
    │
    └── IBBroker.next()         ← processes order status updates
            │
            └── IBStore.placeOrder() / cancelOrder()
```

### Key Design Points

- **IBStore is a singleton** — one IB connection per process. Use different `clientId` values when running multiple processes against the same TWS/Gateway.
- **ib_insync uses asyncio** — `util.patchAsyncio()` and `util.startLoop()` are called during store initialization to enable synchronous use alongside Backtrader's event loop.
- **Historical data splitting** — `reqHistoricalDataEx()` automatically splits large date ranges into multiple IB requests within API limits.
- **Backfilling** — on start or reconnection, `IBData` automatically fetches historical bars to fill the gap before going live.

---

## Supported Timeframes

| Backtrader TimeFrame | Compression | IB Bar Size |
|---------------------|-------------|-------------|
| `Seconds` | 5 | `5 secs` |
| `Seconds` | 10 | `10 secs` |
| `Seconds` | 15 | `15 secs` |
| `Seconds` | 30 | `30 secs` |
| `Minutes` | 1 | `1 min` |
| `Minutes` | 2 | `2 mins` |
| `Minutes` | 3 | `3 mins` |
| `Minutes` | 5 | `5 mins` |
| `Minutes` | 10 | `10 mins` |
| `Minutes` | 15 | `15 mins` |
| `Minutes` | 20 | `20 mins` |
| `Minutes` | 30 | `30 mins` |
| `Hours` | 1 | `1 hour` |
| `Hours` | 2 | `2 hours` |
| `Hours` | 3 | `3 hours` |
| `Hours` | 4 | `4 hours` |
| `Hours` | 8 | `8 hours` |
| `Days` | 1 | `1 day` |
| `Weeks` | 1 | `1 week` |
| `Months` | 1 | `1 month` |

---

## Troubleshooting

**Connection refused**
- Verify TWS or IB Gateway is running
- Check the port matches (`7496` live / `7497` paper)
- Confirm API connections are enabled in TWS settings

**`RuntimeError: Timeout should be used inside a task` (Python 3.14)**
- This is fixed in the current version. Ensure you are using the latest code.

**Historical data returns empty**
- Check `fromdate` / `todate` are within IB's data retention window
- Ensure the contract `dataname` is correctly formatted
- Try `useRTH=False` if data outside regular hours is needed

**Orders not appearing in TWS**
- Confirm `readonly=False` in IBStore
- Verify the `clientId` is not in use by another connection
- Check TWS logs for API error messages

**Multiple strategies or processes**
- Each Python process must use a unique `clientId`
- IBStore is a singleton within a process; you cannot have two IB connections in one process

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

## Related Projects

- [ib_insync](https://github.com/erdewit/ib_insync) — The async IB API wrapper this library is built on
- [Backtrader](https://github.com/mementum/backtrader) — The algorithmic trading framework
- [Interactive Brokers API](https://interactivebrokers.github.io/tws-api/) — Official IB TWS API documentation
