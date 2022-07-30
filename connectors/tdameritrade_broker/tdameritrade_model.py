import time
import typing

from connectors.tdameritrade_broker.tdameritrade_client import TDAmeritradeClient
from constants import *
from models import *
from functools import reduce
from strategies.strategy import Strategy,BreakoutStrategy

import logging
logger = logging.getLogger()


class TDAmeritradeModel:
    def __init__(self, watchlist_quotes: dict = None):
        self.tdameritrade_client = TDAmeritradeClient(self, account_number=OMAR_ACCOUNT_NUMBER, refresh_token=OMAR_REFRESH_TOKEN,
                                                      client_id=CLIENT_ID)
        self._watchlist_quotes = dict() if watchlist_quotes is None else watchlist_quotes

        self.trades: typing.List[Trade] = []
        self.orders: typing.List[Order] = []
        self.strategies: typing.List[Strategy] = []

        self.chart_equities_subscribed_to: list[str] = []





    @property
    def watchlist_quotes(self):
        return self._watchlist_quotes

    @watchlist_quotes.setter
    def watchlist_quotes(self, value):
        self._watchlist_quotes = value

    # only invoked by controller
    def add_symbol_to_watchlist_quotes(self, symbol: str):
        # TODO.. need to validate if the symbol is a valid symbol
        if symbol is not None:
            if symbol not in [*self.watchlist_quotes]:
                self.watchlist_quotes[symbol] = QuoteResponse(data=None, content=None, previous_quote=None)
                comma_separated_symbols = reduce((lambda x, y: f"{x + ',' + y}"), [*self.watchlist_quotes])
                self.tdameritrade_client.subscribe_to_quote(comma_separated_symbols)
                return 'ADDED'
            else:
                raise ValueError(f'{symbol} Symbol is already in the watchlist')
        else:
            raise ValueError(f'Symbol entered is not a valid symbol {symbol}')

    def remove_symbol_from_watchlist_quotes(self, symbol: str):
        if symbol is not None:
            if symbol in [*self.watchlist_quotes]:
                del self.watchlist_quotes[symbol]
                # TODO.. need to unsubscribe from the symbol removed
                # comma_separated_symbols = reduce((lambda x, y: f"{x + ',' + y}"), [*self.watchlist_quotes])
                # self.tdameritrade_client.subscribe_to_quote(comma_separated_symbols)
                return 'REMOVED'
            else:
                raise ValueError(f'{symbol} Symbol is not stored in the watchlist')
        else:
            raise ValueError(f'Symbol entered is not a valid symbol {symbol}')

    def update_quote_of_symbol(self, data):
        contents = data['content']
        for content in contents:
            symbol = content['key']
            if symbol in [*self.watchlist_quotes]:
                previous_quote = self.watchlist_quotes[symbol]
                new_quote = QuoteResponse(data=data, content=content, previous_quote=previous_quote)
                self.watchlist_quotes[symbol] = new_quote
            else:
                return

    def get_realtime_candles_data_of_symbol(self):
        def get_realtime_candles_data_of_symbol(symbol):
            self.chart_equities_subscribed_to.append(symbol)
            comma_separated_symbols = reduce((lambda x, y: f"{x + ',' + y}"), self.chart_equities_subscribed_to)
            self.tdameritrade_client.subscribe_to_chart_equity(comma_separated_symbols)
        return get_realtime_candles_data_of_symbol

    def update_candles_data_of_each_strategy(self, data):
        try:
            contents = data['content']
            for content in contents:
                symbol = content['key']
                for strategy in self.strategies:
                    if strategy.symbol == symbol:
                        strategy.parse_candles(content=content)
        except Exception as e:
            logger.error(f'issue occurred while updating the candles data in the strategies', e)

    def place_buy_limit_order(self, symbol, price, quantity):
        order: Order = self.tdameritrade_client.place_single_order(price=price, quantity=quantity, symbol=symbol,
                                                                   order_type=OrderType.LIMIT,
                                                                   duration=Duration.DAY, instruction=Instruction.BUY)
        if order is not None and order.location:
            self.orders.append(order)
        elif order is None or order.location:
            raise ValueError(f'{OrderType.LIMIT.value} order not placed successfully for this symbol {symbol}, '
                             f'please check the logs and check your brokerage account')

    def place_buy_market_order(self, symbol, quantity):
        order_leg = OrderStrategyRequestPayload.OrderLeg(
            instruction=Instruction.BUY,
            quantity=quantity,
            symbol=symbol,
            asset_type=AssetType.EQUITY
        )
        single_order_payload = SingleOrderRequestPayload(order_type=OrderType.MARKET,
                                                         session=Session.NORMAL,
                                                         duration=Duration.DAY,
                                                         order_leg=order_leg)
        order: Order = self.tdameritrade_client.place_single_order(single_order_payload)
        if order is not None and order.location:
            self.orders.append(order)
        elif order is None or order.location:
            raise ValueError(
                f'{Instruction.BUY.value} {OrderType.MARKET.value} order not placed successfully for this symbol {symbol}, '
                f'please check the logs and check your brokerage account')

    # Also known as an OCO order.
    def place_oco_order(self, symbol: str, first_child_price: float, second_child_price: float, quantity: int,
                        duration: Duration, first_child_order_type: OrderType, second_child_order_type: OrderType,
                        first_child_stop_price: float = None, second_child_stop_price: float = None):

        oco_order_payload = self.create_oco_order_req_payload_obj(duration, first_child_order_type, first_child_price,
                                                                  first_child_stop_price, quantity,
                                                                  second_child_order_type,
                                                                  second_child_price, second_child_stop_price, symbol)

        order: Order = self.tdameritrade_client.place_oco_order(oco_order_payload=oco_order_payload)
        if order is not None and order.location:
            self.orders.append(order)
        elif order is None or order.location:
            raise ValueError(f' order not placed successfully for this symbol {symbol}, '
                             f'please check the logs and check your brokerage account')

    # Also known as 1st Trigger Sequence
    def place_one_order_triggers_another(self, symbol: str, quantity: int, main_order_price: float,
                                         another_order_price: float):

        another_order_leg = OrderStrategyRequestPayload.OrderLeg(symbol=symbol, instruction=Instruction.SELL,
                                                                 quantity=quantity, asset_type=AssetType.EQUITY)

        another_order = SingleOrderRequestPayload(order_leg=another_order_leg, duration=Duration.GOOD_TILL_CANCEL,
                                                  order_type=OrderType.LIMIT, session=Session.NORMAL
                                                  , price=another_order_price)

        main_order_leg = OrderStrategyRequestPayload.OrderLeg(symbol=symbol, instruction=Instruction.BUY,
                                                              quantity=quantity, asset_type=AssetType.EQUITY)

        child_order_strategies = [another_order]
        main_order = TriggerOrderRequestPayload(order_leg=main_order_leg,
                                                duration=Duration.GOOD_TILL_CANCEL, session=Session.NORMAL,
                                                price=main_order_price, order_type=OrderType.LIMIT,
                                                child_order_strategies=child_order_strategies)

        order: Order = self.tdameritrade_client.place_one_order_triggers_another(order=main_order)
        if order is not None and order.location:
            self.orders.append(order)
        elif order is None or order.location:
            raise ValueError(f' order not placed successfully for this symbol {symbol}, '
                             f'please check the logs and check your brokerage account')

    # also knows 1st Trigger OCO order.
    def place_one_order_triggers_oco_order(self, symbol: str, quantity: int, main_order_price: float,
                                           main_order_instruction: Instruction, main_order_type: OrderType,
                                           duration: Duration, first_child_order_type: OrderType, session: Session,
                                           second_child_order_type, first_child_instruction: Instruction,
                                           second_child_instruction: Instruction,
                                           main_order_stop_price: float = None,
                                           first_child_price: float = None, second_child_price: float = None,
                                           first_child_stop_price: float = None, second_child_stop_price: float = None) \
            -> Order:

        oco_order_req_payload = self.create_oco_order_req_payload_obj(duration=duration, symbol=symbol,
                                                                      quantity=quantity, session=session,
                                                                      first_child_order_type=first_child_order_type,
                                                                      second_child_order_type=second_child_order_type,
                                                                      first_child_price=first_child_price,
                                                                      first_child_stop_price=first_child_stop_price,
                                                                      second_child_price=second_child_price,
                                                                      second_child_stop_price=second_child_stop_price,
                                                                      first_child_instruction=first_child_instruction,
                                                                      second_child_instruction=second_child_instruction)

        main_order_leg = OrderStrategyRequestPayload.OrderLeg(symbol=symbol, instruction=main_order_instruction,
                                                              quantity=quantity, asset_type=AssetType.EQUITY)

        child_order_strategies = [oco_order_req_payload]
        main_order = TriggerOrderRequestPayload(order_leg=main_order_leg,
                                                duration=duration, session=session,
                                                price=main_order_price, order_type=main_order_type,
                                                stop_price=main_order_stop_price,
                                                child_order_strategies=child_order_strategies)

        try:
            order: Order = self.tdameritrade_client.place_one_order_triggers_oco_order(main_order)
            if order is not None:
                self.orders.append(order)
                return order
            else:
                raise ValueError(f' 1st Trigger OCO order not placed successfully for this symbol {symbol}, '
                                 f'please check the logs and check your brokerage account')
        except ValueError as value_error:
            raise ValueError(value_error)

    @staticmethod
    def create_oco_order_req_payload_obj(duration, first_child_order_type, first_child_price, first_child_stop_price,
                                         quantity, second_child_order_type, second_child_price, second_child_stop_price,
                                         symbol, session: Session, first_child_instruction: Instruction,
                                         second_child_instruction: Instruction):
        first_child_order_leg = OrderStrategyRequestPayload.OrderLeg(symbol=symbol, instruction=first_child_instruction,
                                                                     quantity=quantity, asset_type=AssetType.EQUITY)
        second_child_order_leg = OrderStrategyRequestPayload.OrderLeg(symbol=symbol,
                                                                      instruction=second_child_instruction,
                                                                      quantity=quantity, asset_type=AssetType.EQUITY)
        first_child_single_order = SingleOrderRequestPayload(order_leg=first_child_order_leg, duration=duration,
                                                             order_type=first_child_order_type, session=session,
                                                             price=first_child_price, stop_price=first_child_stop_price)
        second_child_single_order = SingleOrderRequestPayload(order_leg=second_child_order_leg, duration=duration,
                                                              order_type=second_child_order_type, session=session
                                                              , price=second_child_price,
                                                              stop_price=second_child_stop_price)
        oco_order_payload = OCOOrderRequestPayload(first_child_order=first_child_single_order,
                                                   second_child_order=second_child_single_order)
        return oco_order_payload

    def activate_automated_trading_strategy(self):
        breakout_strategy_1 = BreakoutStrategy(symbol='TQQQ',
                                             get_realtime_candles_data_of_symbol=self.get_realtime_candles_data_of_symbol())
        self.strategies.append(breakout_strategy_1)

        time.sleep(5)
        breakout_strategy_2 = BreakoutStrategy(symbol='TSLA',
                                             get_realtime_candles_data_of_symbol=self.get_realtime_candles_data_of_symbol())
        self.strategies.append(breakout_strategy_2)

