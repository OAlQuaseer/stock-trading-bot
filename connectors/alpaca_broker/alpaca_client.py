from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream, StockDataStream
from alpaca.data.models import Trade
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import Order
from alpaca.data.enums import DataFeed

import talib as ta
import pandas as pd
import websocket
import threading
import logging
import datetime
import time
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# to show the logs on the console we need to initialize and configure a stream handler
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# to print the logs on a file we need to initialize and configure a file handler
date_in_str = str(datetime.datetime.now().date())
file_handler = logging.FileHandler(f'./../../logs/{date_in_str}.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 600)


class AlpacaSDKClient:
    def __init__(self):
        self.paper_api_endpoint = 'https://paper-api.alpaca.markets'
        self.API_KEY = 'PK5WWYWN5SA53KO74CYD'
        self.SECRET_KEY = '4xl5fDgTKjeFx5EMsOGjZf7uxPulZPNjNCbO9tau'
        # crypto
        self.crypto_hist_data_client = CryptoHistoricalDataClient()
        self.crypto_stream = CryptoDataStream(self.API_KEY, self.SECRET_KEY)
        # stock
        self.stock_hist_data_client = StockHistoricalDataClient(self.API_KEY, self.SECRET_KEY)

        self.stock_stream = StockDataStream(self.API_KEY, self.SECRET_KEY)
        self.stock_paper_trading_client = TradingClient(self.API_KEY, self.SECRET_KEY, paper=True)

    # ######################################## Crypto methods ###############################################

    def get_crypto_historical_data(self):
        # Creating request object
        request_params = CryptoBarsRequest(
            symbol_or_symbols=["BTC/USD"],
            timeframe=TimeFrame.Day,
            start=datetime.datetime(2023, 1, 1),
            end=datetime.datetime(2023, 1, 10)
        )
        return self.crypto_hist_data_client.get_crypto_bars(request_params).df

    @staticmethod
    async def crypto_bar_callback(bar):
        for property_name, value in bar:
            print(f"\"{property_name}\": {value}")

    def subscribe_crypto_bars(self, symbol):
        self.crypto_stream.subscribe_bars(self.crypto_bar_callback, symbol)

    def run_crypto_stream(self):
        self.crypto_stream.run()

    # ######################################## Stocks Historical data methods ##########################################

    def get_stock_historical_data(self, symbol_or_symbols, timeframe, start=None, end=None, limit=None):
        start_time = time.time()
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_or_symbols,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit
        )
        response_df = self.stock_hist_data_client.get_stock_bars(request_params).df
        logger.info(f'seconds taken to fetch:{time.time() - start_time}')
        return response_df

    # ################################# Stocks Data Streaming #####################################################

    def subscribe_stock_bars(self, symbol):
        self.stock_stream.subscribe_bars(self.stock_bar_callback, symbol)

    async def stock_bar_callback(self, bar):
        for property_name, value in bar:
            print(f"\"{property_name}\": {value}")

    def subscribe_to_trade_schema(self, symbol, callback=None):
        async def default_callback(trade: Trade):
            for property_name, value in trade:
                print(f"\"{property_name}\": {value}")
        callback = callback if callback is not None else default_callback
        self.stock_stream.subscribe_trades(callback, symbol)

    def run_stock_stream(self):
        self.stock_stream.run()

    # ############## trading APIs ######################################################################
    def place_stock_market_order(self, symbol):
        # preparing market order
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=100,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        response: Order = self.stock_paper_trading_client.submit_order(order_data=market_order_data)
        logger.info('Market order submitted with order id: ' + str(response.id))
        return response

class Strategy:
    def __init__(self):
        pass


class AlpacaClient:
    def __init__(self):
        self.ws_endpoint = 'wss://stream.data.alpaca.markets/v2/'
        self.API_KEY = 'PK5WWYWN5SA53KO74CYD'
        self.SECRET_KEY = '4xl5fDgTKjeFx5EMsOGjZf7uxPulZPNjNCbO9tau'

        # private attributes
        self._thread = None
        self._ws = None

    def establish_ws_connection(self):
        self._ws = None
        self._thread = threading.Thread(target=self.start_ws_connection)
        self._thread.start()

    def on_open(self, ws):
        logger.info("Connection opened")
        ws_request = {"action": "auth", "key": self.API_KEY, "secret": self.SECRET_KEY}
        self._ws.send(data=json.dumps(ws_request))

    def on_message(self, ws, message):
        logger.info("message received: " + message)

    def on_error(self, ws, error):
        logger.error("Error occurred in on_error method: " + error)

    def on_close(self):
        logger.info("connection closed")

    def start_ws_connection(self):
        websocket.enableTrace(False)
        self._ws = websocket.WebSocketApp(self.ws_endpoint + 'iex',
                                          on_open=self.on_open,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)

        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error('error in run_forever() method: %s', e)
                time.sleep(2)


if __name__ == '__main__':
    logger.info('_____alpaca_client_main_____')

    # stream data through the SDK
    alpaca_sdk_client = AlpacaSDKClient()
    # alpaca_sdk_client.subscribe_to_trade_schema('TQQQ')
    alpaca_sdk_client.subscribe_stock_bars('TQQQ')
    # alpaca_sdk_client.run_stock_stream()

    # alpaca_client = AlpacaClient()
    # alpaca_client.establish_ws_connection()

    #

    tqqq_df = alpaca_sdk_client.get_stock_historical_data(['TQQQ'], TimeFrame.Minute)
    start_time = time.time()
    tqqq_df['9_day_ema'] = ta.EMA(tqqq_df['close'], timeperiod=9)
    tqqq_df['21_day_ema'] = ta.EMA(tqqq_df['close'], timeperiod=21)
    logger.info(f'here ---- {time.time() - start_time}')
    # alpaca_sdk_client.place_stock_market_order(symbol='TQQQ')
    print(tqqq_df)
