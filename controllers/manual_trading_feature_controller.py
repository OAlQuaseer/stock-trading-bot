import time

from connectors.tdameritrade_broker.tdameritrade_model import TDAmeritradeModel
from interface.manual_trading_component import ManualTradingComponent
from models import *
import logging


logger = logging.getLogger()


class ManualTradingFeatureController:
    def __init__(self, model: TDAmeritradeModel, view: ManualTradingComponent):
        self.model = model
        self.view = view

        # TODO... to remove
        #time.sleep(5)
        #self.activate_automated_trading_strategy()

    def add_stock_to_trade(self):
        symbols_to_trade = self.model.watchlist_quotes.keys()
        self.view.lower_frame.create_widgets_for_stock_trading_inputs(symbols_to_trade)

    def activate_manual_trading_strategy(self, user_inputs):
        symbol = user_inputs['symbol']
        balance = user_inputs['balance']
        quantity = user_inputs['quantity']
        last_traded_price_flag = user_inputs['last_traded_price_flag']
        entry_point = user_inputs['entry_point']
        try:
            if last_traded_price_flag is True:
                last_price = self.model.watchlist_quotes[symbol].last_price
                stop_loss = round(last_price - user_inputs['stop_loss'], 2)
                profit_target = round(user_inputs['profit_target'] + last_price, 2)
                last_price = round(last_price, 2)
                order: Order = self.model.place_one_order_triggers_oco_order(symbol=symbol, quantity=quantity, main_order_price=last_price,
                                                        main_order_type=OrderType.LIMIT, main_order_instruction=Instruction.BUY,
                                                        first_child_order_type=OrderType.LIMIT, first_child_stop_price=None,
                                                        first_child_instruction=Instruction.SELL, first_child_price=profit_target,
                                                        second_child_instruction=Instruction.SELL, second_child_order_type=OrderType.STOP,
                                                        second_child_price=None, second_child_stop_price=stop_loss,
                                                        session=Session.NORMAL, duration=Duration.GOOD_TILL_CANCEL)
            elif last_traded_price_flag is False and entry_point > 0:
                stop_loss = round(entry_point - user_inputs['stop_loss'], 2)
                profit_target = round(user_inputs['profit_target'] + entry_point, 2)
                entry_point = round(entry_point, 2)
                order: Order = self.model.place_one_order_triggers_oco_order(symbol=symbol, quantity=quantity,
                                                                             main_order_price=entry_point,
                                                                             main_order_stop_price=entry_point,
                                                                             main_order_type=OrderType.STOP_LIMIT,
                                                                             main_order_instruction=Instruction.BUY,
                                                                             first_child_order_type=OrderType.LIMIT,
                                                                             first_child_stop_price=None,
                                                                             first_child_instruction=Instruction.SELL,
                                                                             first_child_price=profit_target,
                                                                             second_child_instruction=Instruction.SELL,
                                                                             second_child_order_type=OrderType.STOP,
                                                                             second_child_price=None,
                                                                             second_child_stop_price=stop_loss,
                                                                             session=Session.NORMAL,
                                                                             duration=Duration.GOOD_TILL_CANCEL)
            else:
                order = None
            if order.location is not None:
                logger.info(f'Manual strategy order placed successfully with this location id {order.location}')
        except ValueError as value_error:
            # TODO...show an error message on UI
            logger.error(f"Value error exception thrown in {self.activate_manual_trading_strategy.__name__}: {value_error}")

    def activate_automated_trading_strategy(self):
        try:
            self.model.activate_automated_trading_strategy()
        except ValueError as value_error:
            logger.error('to be added')

