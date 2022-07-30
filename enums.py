from enum import Enum

class Direction(Enum):
    UP = 'up'
    DOWN = 'down'

class Change(Enum):
    PERCENT = 'percent'
    CHANGE = 'change'

class Index(Enum):
    COMPX = '$COMPX'
    DJI = '$DJI'
    SPX = '$SPX.X'


class OrderType(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP = 'STOP'
    STOP_LIMIT = 'STOP_LIMIT'
    TRAILING_STOP = 'TRAILING_STOP'
    MARKET_ON_CLOSE = 'MARKET_ON_CLOSE'
    EXERCISE = 'EXERCISE'
    TRAILING_STOP_LIMIT = 'TRAILING_STOP_LIMIT'
    NET_DEBIT = 'NET_DEBIT'
    NET_CREDIT = 'NET_CREDIT'
    NET_ZERO = 'NET_ZERO'


class Session(Enum):
    NORMAL = 'NORMAL'


class Duration(Enum):
    DAY = 'DAY'
    GOOD_TILL_CANCEL = 'GOOD_TILL_CANCEL'
    FILL_OR_KILL = 'FILL_OR_KILL'


class OrderStrategyType(Enum):
    SINGLE = 'SINGLE'
    TRIGGER = 'TRIGGER'
    OCO = 'OCO'


class Instruction(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class PositionSide(Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'


class AssetType(Enum):
    EQUITY = 'EQUITY'

