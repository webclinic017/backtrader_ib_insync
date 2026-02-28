"""backtrader_ib_insync — Interactive Brokers integration for Backtrader.

This package bridges the `ib_insync` async IB API with the Backtrader
algorithmic trading framework.  It exposes three public classes:

``IBStore``
    Singleton that owns the ``ib_insync.IB`` connection to TWS / IB Gateway.
    All data feeds and the broker share this one connection.  Handles
    historical data requests, real-time bar/tick subscriptions, order
    placement, and account value updates.

``IBBroker``
    Implements Backtrader's ``BrokerBase`` interface.  Translates
    ``buy()`` / ``sell()`` calls into IB orders, tracks their lifecycle, and
    feeds notifications back to Cerebro strategies.

``IBData``
    Implements Backtrader's ``DataBase`` interface.  Delivers OHLCV bars to a
    Cerebro strategy from either a historical download, live 5-second RTBars,
    or live RTVolume ticks.

Typical usage::

    import backtrader as bt
    import backtrader_ib_insync as ibnew

    store  = ibnew.IBStore(host='127.0.0.1', port=7497, clientId=1)
    data   = store.getdata(dataname='AAPL-STK-SMART-USD',
                           timeframe=bt.TimeFrame.Minutes, compression=1)
    broker = store.getbroker()

    cerebro = bt.Cerebro()
    cerebro.setbroker(broker)
    cerebro.adddata(data)
    cerebro.addstrategy(MyStrategy)
    cerebro.run()
"""
from .ibstore import IBStore
from .ibbroker import IBBroker
from .ibdata import IBData
