import logging
import time

from enums import *
import typing
from models import *
import threading

logger = logging.getLogger()


class Strategy:
    def __init__(self, symbol: str, get_realtime_candles_data_of_symbol):
        self.symbol = symbol
        self._get_realtime_candles_data_of_symbol = get_realtime_candles_data_of_symbol
        self.candles: typing.List[Candle] = []
        self.signals: list = []

        self.subscribe_to_streams()

    # Subscribe to the streams needed to collect all the data needed in the strategy calculation
    def subscribe_to_streams(self):
        self._get_realtime_candles_data_of_symbol(self.symbol)

    def parse_candles(self, content):
        candle = Candle(content)
        self.candles.append(candle)


class BreakoutStrategy(Strategy):
    def __init__(self, symbol, get_realtime_candles_data_of_symbol, min_volume: int = None):
        super().__init__(symbol, get_realtime_candles_data_of_symbol)
        self._min_volume = 10000
        logger.info(f'Breakout strategy activated for this symbol {symbol}')
        self._thread = threading.Thread(target=self.check_signal)
        self._thread.start()

    # to determine if we need to enter a long trade or short trade or do nothing
    def check_signal(self) -> typing.Union[PositionSide, None]:
        if len(self.candles) < 2:
            print(len(self.candles))
            time.sleep(30)
            self.check_signal()
        if self.candles[-1].close_price > self.candles[-2].high_price and self.candles[-1].volume > self._min_volume:
            # Long trade
            print(PositionSide.LONG.value)
            return PositionSide.LONG
        elif self.candles[-1].close_price < self.candles[-2].low_price and self.candles[-1].volume > self._min_volume:
            # Short trade
            print(PositionSide.SHORT.value)
            return PositionSide.SHORT
        else:
            print('Nothing')
            time.sleep(30)
            self.check_signal()

