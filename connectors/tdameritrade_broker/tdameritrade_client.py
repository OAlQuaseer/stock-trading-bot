import typing
from requests import request, Response
from api_end_points import *
from models import *
from enums import *
import websocket
import threading
import time
import datetime
import dateutil.parser as dp
import json
from urllib.parse import urlencode
import logging

logger = logging.getLogger()


# TODO... need to fix the circular import
# from connectors.tdameritrade_broker.tdameritrademodel import TDAmeritradeModel


class TDAmeritradeClient:
    def __init__(self, tdameritrade_model, account_number, refresh_token, client_id):
        self.account_number = str(account_number)
        self.refresh_token = refresh_token
        self.client_id = client_id

        # info needed from the brokerage at the stage of initialization
        self._access_token = self.get_access_token_by_refresh_token()
        self.projected_balances = self.get_account_balances()
        self.user_principals = self.get_user_principals()
        self.tdameritrade_model = tdameritrade_model

        # private attributes
        self._ws = None
        self._thread = threading.Thread(target=self.start_ws_connection)
        self._thread.start()

        self._fetch_new_access_token_thread = threading.Thread(target=self.fetch_new_access_token)
        self._fetch_new_access_token_thread.start()

    @staticmethod
    def _make_https_request(method, api_end_point, params=None, headers=None, data=None, json_data=None):
        try:
            response: Response = request(method, BASE_RESOURCE_URL + api_end_point, params=params, headers=headers,
                                         data=data, json=json_data)
        except Exception as e:
            logger.error(f'error happened when submitting a request to the server', e)
            return None

        if response is not None:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response
            else:
                raise ValueError(f'response status code: {response.status_code}, response text: {response.text}')

        return None

    # Access token for authentication
    def get_access_token_by_refresh_token(self):
        data = dict()
        data['grant_type'] = 'refresh_token'
        data['refresh_token'] = self.refresh_token
        data['client_id'] = self.client_id
        data['access_type'] = ''
        data['redirect_uri'] = ''
        data['code'] = ''
        result = self._make_https_request('POST', api_end_point=POST_ACCESS_TOKEN, data=data)
        return result['access_token'] if result else None

    def get_account_balances(self) -> ProjectedBalances:
        api_end_point = GET_ACCOUNT + self.account_number
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        result = self._make_https_request('GET', api_end_point, headers=headers)
        if result is not None:
            projected_balances_data = result['securitiesAccount']['projectedBalances']
            projected_balances = ProjectedBalances(projected_balances_data)
            return projected_balances
        else:
            return None

    def get_movers_for_particular_market(self, index: Index, direction: Direction, change: Change):
        api_end_point = GET_MOVERS + index.value + '/movers'
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        params = dict()
        params['direction'] = direction.value
        params['change'] = change.value
        result = self._make_https_request('GET', api_end_point, headers=headers, params=params)
        if result is not None:
            return result
        else:
            return None

    def get_user_principals(self, fields: str = None):
        api_end_point = GET_USER_PRINCIPALS
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        params = dict()
        params['fields'] = fields or 'streamerSubscriptionKeys,streamerConnectionInfo'
        result = self._make_https_request('GET', api_end_point, headers=headers, params=params)
        if result is not None:
            return UserPrincipals(result)
        else:
            return None

    # for now its supporting only Equities..TODO.. need to add options
    def place_single_order(self, order: SingleOrderRequestPayload) -> typing.Union[Order, None]:
        api_end_point = GET_ACCOUNT + self.account_number + PLACE_ORDER
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        try:
            result = self._make_https_request('POST', api_end_point=api_end_point, headers=headers,
                                              json_data=order.to_json)
            if result is not None:
                order: Order = Order(location=result.headers.get('Location'),
                                     order_strategy_type=order.order_strategy_type, symbol=order.order_leg.symbol)
                return order
            else:
                return None
        except Exception as e:
            return None

    def place_oco_order(self, oco_order_payload: OCOOrderRequestPayload) -> typing.Union[None, Order]:
        api_end_point = GET_ACCOUNT + self.account_number + PLACE_ORDER
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        try:
            result = self._make_https_request('POST', api_end_point=api_end_point, headers=headers,
                                              json_data=oco_order_payload.to_json)
            if result is not None:
                order: Order = Order(location=result.headers.get('Location'), order_strategy_type=oco_order_payload.order_strategy_type,
                                     symbol=oco_order_payload.first_child_order.order_leg.symbol)
                return order
            else:
                return None
        except Exception as e:
            return None

    def place_one_order_triggers_another(self, order: TriggerOrderRequestPayload):
        api_end_point = GET_ACCOUNT + self.account_number + PLACE_ORDER
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        try:
            result = self._make_https_request('POST', api_end_point=api_end_point, headers=headers,
                                              json_data=order.to_json)
            if result is not None:
                order: Order = Order(location=result.headers.get('Location'),
                                     order_strategy_type=order.order_strategy_type,
                                     symbol=order.order_leg.symbol)
                return order
            else:
                return None
        except Exception as e:
            return None

    def place_one_order_triggers_oco_order(self, order: TriggerOrderRequestPayload):
        api_end_point = GET_ACCOUNT + self.account_number + PLACE_ORDER
        headers = dict()
        headers['Authorization'] = f'Bearer {self._access_token}'
        try:
            result = self._make_https_request('POST', api_end_point=api_end_point, headers=headers,
                                              json_data=order.to_json)
            if result is not None:
                order: Order = Order(location=result.headers.get('Location'),
                                     order_strategy_type=order.order_strategy_type,
                                     symbol=order.order_leg.symbol)
                return order
            else:
                return None
        except ValueError as value_error:
            raise ValueError(value_error)
        except Exception as e:
            logger.error(f'issue occurred in this method {self.place_one_order_triggers_oco_order.__name__}', e)
            return None

    def fetch_new_access_token(self):
        while True:
            try:
                time.sleep(600)
                self._access_token = self.get_access_token_by_refresh_token()
                logger.info('new access token fetched')
                self.fetch_new_access_token()
            except Exception as e:
                logger.error(f'error occurred while fetching a new access token')
                time.sleep(2)
                self.fetch_new_access_token()


    def start_ws_connection(self):
        websocket.enableTrace(False)

        self._ws = websocket.WebSocketApp("wss://" + self.user_principals.streamer_socket_url + "/ws",
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

    def on_message(self, ws, message):
        # print(message)
        if message is not None:
            converted_message: dict = json.loads(message)
        else:
            return

        if converted_message.get('data'):
            for data in converted_message.get('data'):
                if data['service'] == 'QUOTE':
                    self.tdameritrade_model.update_quote_of_symbol(data)
                elif data['service'] == 'CHART_EQUITY':
                    self.tdameritrade_model.update_candles_data_of_each_strategy(data)
                elif data['service'] == 'ACTIVES_NASDAQ':
                    content = data['content']
        elif converted_message.get('response'):
            pass
        elif converted_message.get('notify'):
            pass
        else:
            return None

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        token_time_stamp = self.user_principals.token_time_stamp
        token_time_stamp_parsed = dp.parse(token_time_stamp)
        token_time_stamp_in_ms = int(token_time_stamp_parsed.timestamp() * 1000)
        credentials = {
            "userid": self.user_principals.account,
            "token": self.user_principals.token,
            "company": self.user_principals.company,
            "segment": self.user_principals.segment,
            "cddomain": self.user_principals.accountCdDomainId,
            "usergroup": self.user_principals.userGroup,
            "accesslevel": self.user_principals.access_level,
            "authorized": "Y",
            "timestamp": token_time_stamp_in_ms,
            "appid": self.user_principals.source,
            "acl": self.user_principals.acl
        }
        ws_request = {
            "requests": [
                {
                    "service": "ADMIN",
                    "command": "LOGIN",
                    "requestid": 0,
                    "account": self.user_principals.account,
                    "source": self.user_principals.source,
                    "parameters": {
                        "credential": urlencode(credentials),
                        "token": self.user_principals.token,
                        "version": "1.0"
                    }
                }
            ]
        }
        self._ws.send(data=json.dumps(ws_request))
        print("Opened connection")

    def subscribe_to_actives(self):
        actives_nasdaq_all_req = ActivesRequest(self.user_principals, service="ACTIVES_NASDAQ", command="SUBS",
                                                request_id=1, param_keys='NASDAQ-ALL', param_fields='0,1')
        self._subscribe_to_stream(actives_nasdaq_all_req)

    def _subscribe_to_stream(self, req: TDAmeritradeWebSocketStreamRequest):
        ws_request = {
            "requests": [
                req.request
            ]
        }
        self._ws.send(data=json.dumps(ws_request))

    def subscribe_to_chart_equity(self, symbol: str):
        chart_equity_req = ChartEquityRequest(self.user_principals, service="CHART_EQUITY", command="SUBS",
                                              request_id=2,
                                              param_keys=symbol, param_fields="0,1,2,3,4,5,6,7,8")
        self._subscribe_to_stream(chart_equity_req)

    def subscribe_to_quote(self, symbol: str, request_id=5):
        quote_req = QuoteRequest(self.user_principals, request_id=request_id, param_keys=symbol,
                                 param_fields="0,1,2,3,4,5,6,7,8,9,17,18")
        self._subscribe_to_stream(quote_req)
