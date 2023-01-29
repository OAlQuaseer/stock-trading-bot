
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream, StockDataStream


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


class AlpacaSDKClient:
    def __init__(self):
        self.api_endpoint = 'https://paper-api.alpaca.markets'
        self.API_KEY = 'PK5WWYWN5SA53KO74CYD'
        self.SECRET_KEY = '4xl5fDgTKjeFx5EMsOGjZf7uxPulZPNjNCbO9tau'
        # crypto
        self.client = CryptoHistoricalDataClient()
        self.crypto_stream = CryptoDataStream(self.API_KEY, self.SECRET_KEY)
        # stocks
        self.stocks_stream = StockDataStream(self.API_KEY, self.SECRET_KEY)

    def get_historical_data(self):
        # Creating request object
        request_params = CryptoBarsRequest(
            symbol_or_symbols=["BTC/USD"],
            timeframe=TimeFrame.Day,
            start=datetime.datetime(2023, 1, 1),
            end=datetime.datetime(2023, 1, 10)
        )
        return self.client.get_crypto_bars(request_params).df

    @staticmethod
    async def bar_callback(bar):
        for property_name, value in bar:
            print(f"\"{property_name}\": {value}")

    def subscribe_crypto_bars(self, symbol):
        self.crypto_stream.subscribe_bars(self.bar_callback, symbol)

    def run_crypto_stream(self):
        self.crypto_stream.run()


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
    # alpaca_sdk_client = AlpacaSDKClient()
    # alpaca_sdk_client.subscribe_crypto_bars("BTC/USD")
    # alpaca_sdk_client.run_crypto_stream()

    alpaca_client = AlpacaClient()
    alpaca_client.establish_ws_connection()







