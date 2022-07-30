import json
import typing
from enums import *


class ProjectedBalances:
    def __init__(self, projected_balances_data: dict):
        self.available_funds = projected_balances_data['availableFunds']
        self.available_funds_non_marginable_trade = projected_balances_data['availableFundsNonMarginableTrade']
        self.buying_power = projected_balances_data['buyingPower']
        self.day_trading_buying_power = projected_balances_data['dayTradingBuyingPower']
        self.day_trading_buying_power_call = projected_balances_data['dayTradingBuyingPowerCall']
        self.is_in_call = projected_balances_data['isInCall']
        self.maintenance_call = projected_balances_data['maintenanceCall']
        self.reg_t_call = projected_balances_data['regTCall']
        self.stock_buying_power = projected_balances_data['stockBuyingPower']


class UserPrincipals:
    def __init__(self, user_principals_data: dict):
        self.streamer_socket_url = user_principals_data['streamerInfo']['streamerSocketUrl']
        self.token_time_stamp = user_principals_data['streamerInfo']['tokenTimestamp']
        self.account = user_principals_data['accounts'][0]['accountId']
        self.source = user_principals_data['streamerInfo']['appId']
        self.token = user_principals_data['streamerInfo']['token']
        self.company = user_principals_data['accounts'][0]['company']
        self.segment = user_principals_data['accounts'][0]['segment']
        self.accountCdDomainId = user_principals_data['accounts'][0]['accountCdDomainId']
        self.userGroup = user_principals_data['streamerInfo']['userGroup']
        self.access_level = user_principals_data['streamerInfo']['accessLevel']
        self.acl = user_principals_data['streamerInfo']['acl']


class Order:
    def __init__(self, symbol, order_strategy_type: OrderStrategyType, location: str):
        self.symbol = symbol
        self.order_strategy_type = order_strategy_type
        self.location = location


class Trade:
    def __init__(self, symbol, entry_point: float, exit_point: float):
        self.symbol = symbol
        self.entry_point = entry_point
        self.exit_point = exit_point


class Candle:
    def __init__(self, candle_data: dict):
        self.open_price = candle_data['1']
        self.high_price = candle_data['2']
        self.low_price = candle_data['3']
        self.close_price = candle_data['4']
        self.volume = candle_data['5']
        self.sequence = candle_data['6']
        self.chart_time = candle_data['7']
        self.chart_day = candle_data['8'] # Not useful as per tdameritrade docs


class Signal:
    def __init__(self, candle: Candle, entry_price: float, exit_price: float, position_side: PositionSide):
        self.candle_where_signal_generated = candle
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.position_side = position_side


class TDAmeritradeWebSocketStreamRequest:
    def __init__(self, user_principals: UserPrincipals, request: dict):
        self._request: dict = {"account": user_principals.account, "source": user_principals.source} \
                              | request

    @property
    def request(self) -> dict:
        return self._request


class TDAmeritradeWebSocketStreamResponse:
    def __init__(self, data: dict):
        if data is not None:
            self.timestamp = data['timestamp']
            self.command = data['command']
            self.service = data['service']
        else:
            self.timestamp = None
            self.command = None
            self.service = None


class ActivesRequest(TDAmeritradeWebSocketStreamRequest):
    def __init__(self, user_principals: UserPrincipals,
                 service: str, command: str, request_id: int, param_keys: str,
                 param_fields: str):
        super().__init__(user_principals, {
            "service": service,
            "requestid": request_id,
            "command": command,
            "parameters": {
                "keys": param_keys,
                "fields": param_fields
            }
        }
                         )


class ChartEquityRequest(TDAmeritradeWebSocketStreamRequest):
    def __init__(self, user_principals: UserPrincipals,
                 service: str, command: str, request_id: int, param_keys: str,
                 param_fields: str):
        super().__init__(user_principals,
                         {
                             "service": service,
                             "requestid": request_id,
                             "command": command,
                             "parameters": {
                                 "keys": param_keys.upper(),
                                 "fields": param_fields
                             }
                         }
                         )


class QuoteRequest(TDAmeritradeWebSocketStreamRequest):
    def __init__(self, user_principals: UserPrincipals, request_id: int, param_keys: str,
                 param_fields: str):
        super().__init__(user_principals, {
            "service": "QUOTE",
            "requestid": request_id,
            "command": "SUBS",
            "parameters": {
                "keys": param_keys.upper(),
                "fields": param_fields
            }
        }
                         )


class QuoteResponse(TDAmeritradeWebSocketStreamResponse):
    def __init__(self, data: dict = None, content: dict = None,
                 previous_quote: typing.Union['QuoteResponse', 'None'] = None):
        super().__init__(data)
        if content is not None:
            self.key = content['key']
            self.delayed = bool(content['delayed']) if 'delayed' in content else previous_quote.delayed
            self.bid_price = float(content['1']) if '1' in content else previous_quote.bid_price
            self.ask_price = float(content['2']) if '2' in content else previous_quote.ask_price
            self.last_price = float(content['3']) if '3' in content else previous_quote.last_price  # Price at which the last trade was matched
            self.bid_size = float(content['4']) if '4' in content else previous_quote.bid_size
            self.ask_size = float(content['5']) if '5' in content else previous_quote.ask_size
            self.ask_id = content['6'] if '6' in content else previous_quote.ask_id
            self.bid_id = content['7'] if '7' in content else previous_quote.bid_id
            self.total_volume = int(content['8']) if '8' in content else previous_quote.total_volume
            self.last_size = float(content['9']) if '9' in content else previous_quote.last_size
            self.marginable = bool(content['17']) if '17' in content else previous_quote.marginable
            self.shortable = bool(content['18']) if '18' in content else previous_quote.shortable
        else:
            self.key = None
            self.delayed = None
            self.bid_price = None
            self.ask_price = None
            self.last_price = None
            self.bid_size = None
            self.ask_size = None
            self.ask_id = None
            self.bid_id = None
            self.total_volume = None
            self.last_size = None
            self.marginable = None
            self.shortable = None


class OrderStrategyRequestPayload:
    def __init__(self, order_strategy_type: OrderStrategyType,
                 session: Session = None,
                 duration: Duration = None,
                 order_type: OrderType = None,
                 price: float = None,
                 stop_price: float = None):

        self.order_strategy_type = order_strategy_type
        self.session = session
        self.duration = duration
        self.order_type = order_type
        self.price = price
        self.stop_price = stop_price

    @property
    def to_json(self):
        price_dict = {"price": self.price} if self.price is not None else {}
        session_dict = {"session": self.session.value} if self.session is not None else {}
        duration_dict = {"duration": self.duration.value} if self.duration is not None else {}
        order_type_dict = {"orderType": self.order_type.value} if self.order_type is not None else {}
        stop_price = {"stopPrice": self.stop_price} if self.stop_price is not None else {}
        return price_dict | session_dict | duration_dict | order_type_dict | stop_price | {
            "orderStrategyType": self.order_strategy_type.value,
        }

    class OrderLeg:
        def __init__(self, symbol, asset_type: AssetType, instruction: Instruction, quantity: int):
            self.instruction = instruction
            self.symbol = symbol
            self.asset_type = asset_type
            self.quantity = quantity

        @property
        def to_json(self):
            return {
                "instruction": self.instruction.value,
                "quantity": self.quantity,
                "instrument": {
                    "symbol": self.symbol,
                    "assetType": self.asset_type.value
                }
            }


class SingleOrderRequestPayload(OrderStrategyRequestPayload):
    def __init__(self, order_type: OrderType,
                 session: Session,
                 duration: Duration,
                 order_leg: OrderStrategyRequestPayload.OrderLeg,
                 price: float = None,
                 stop_price: float = None):
        super().__init__(order_strategy_type=OrderStrategyType.SINGLE, session=session, duration=duration,
                         order_type=order_type, price=price, stop_price=stop_price)
        self.order_leg = order_leg

    @property
    def to_json(self):
        return super().to_json | {
            "orderLegCollection": [self.order_leg.to_json]
        }


class TriggerOrderRequestPayload(OrderStrategyRequestPayload):
    def __init__(self,
                 order_type: OrderType,
                 session: Session,
                 duration: Duration,
                 order_leg: OrderStrategyRequestPayload.OrderLeg,
                 child_order_strategies: list,
                 price: float = None,
                 stop_price: float = None):
        super().__init__(order_strategy_type=OrderStrategyType.TRIGGER, session=session, duration=duration,
                         order_type=order_type, price=price, stop_price=stop_price)
        self.order_leg = order_leg
        self.child_order_strategies = child_order_strategies

    @property
    def to_json(self):
        return super().to_json | {
            "orderLegCollection": [self.order_leg.to_json]
        } | {
            'childOrderStrategies': [strategy.to_json for strategy in self.child_order_strategies]
        }


class OCOOrderRequestPayload(OrderStrategyRequestPayload):
    def __init__(self, first_child_order: SingleOrderRequestPayload,
                 second_child_order: SingleOrderRequestPayload):
        super().__init__(order_strategy_type=OrderStrategyType.OCO)
        self.first_child_order = first_child_order
        self.second_child_order = second_child_order

    @property
    def to_json(self):
        return super().to_json | {
            'childOrderStrategies': [
                self.first_child_order.to_json,
                self.second_child_order.to_json
            ]
        }




