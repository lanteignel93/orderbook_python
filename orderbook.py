import bisect
import itertools
import datetime
import pprint
from collections import ChainMap
from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderBookDic(ChainMap):
    "Variant of ChainMap that allows direct updates to inner scopes"

    def __setitem__(self, key, value):
        for mapping in self.maps:
            if key in mapping:
                mapping[key] = value
                return
        self.maps[0][key] = value

    def __delitem__(self, key):
        for mapping in self.maps:
            if key in mapping:
                del mapping[key]
                return
        raise KeyError(key)


class Order:
    id_iter = itertools.count()

    def __init__(self, price: float, time: datetime.datetime, side: OrderSide) -> None:
        self.price = price
        self.time = time
        self.side = side
        self.id = next(self.id_iter)

    def __repr__(self) -> str:
        return f"Order(price={self.price:.4f}$, {self.time}, side={self.side.value}, id={self.id})"


class OrderBook:
    def __init__(self):
        self._ask: list = []
        self._bid: list = []
        self._buy_dic: dict = {}
        self._sell_dic: dict = {}
        self._hash_map: OrderBookDic = OrderBookDic(self._buy_dic, self._sell_dic)

    @property
    def ask(self):
        return self._ask

    @property
    def bid(self):
        return self._bid

    @property
    def hash_map(self):
        return self._hash_map

    @property
    def buy_dic(self):
        return self._buy_dic

    @property
    def sell_dic(self):
        return self._sell_dic

    def __call__(self, *args, **kwargs):
        if len(kwargs) == 0 and len(args) == 0:
            self.hash_map

        if len(kwargs) > 0 and len(args) > 0 or len(kwargs) > 1 or len(args) > 1:
            raise ValueError("Only one input is valid.")

        if len(kwargs) == 1:
            try:
                type = kwargs.pop("type")

            except KeyError:
                raise KeyError("Wrong keyword argument, only type allowed.")

        if len(args) == 1 and len(kwargs) == 0:
            type = args[0]

        if type == "buy":
            return self.buy_dic

        elif type == "sell":
            return self.sell_dic

        else:
            raise KeyError("Type must be either 'buy' or 'sell'")

    def insert(self, order: list[Order] | Order) -> None:
        if isinstance(order, list):
            for o in order:
                self._insert(o)

        elif isinstance(order, Order):
            self._insert(order)
        else:
            raise ValueError("Wrong Input Type, must be Order or list of Order")

    def _insert(self, order: Order) -> None:
        match order.side:
            case OrderSide.BUY:
                bisect.insort_left(self.bid, order, key=lambda x: (-x.price, x.time))
                self.buy_dic[order.id] = order
            case OrderSide.SELL:
                bisect.insort_left(self.ask, order, key=lambda x: (x.price, x.time))
                self.sell_dic[order.id] = order
            case _:
                raise NotImplementedError("Wrong Side, needs to buy BUY or SELL.")

        return None

    def pop(self, side: OrderSide) -> Order | None:
        match side:
            case OrderSide.BUY:
                if len(self.bid) == 0:
                    return None

                val = self.bid[0]
                self.bid.remove(self.bid[0])

            case OrderSide.SELL:
                if len(self.ask) == 0:
                    return None

                val = self.ask[0]
                self.ask.remove(self.ask[0])

            case _:
                raise NotImplementedError("Wrong Side, needs to buy BUY or SELL.")
        try:
            del self.hash_map[val.id]
        except KeyError:
            raise KeyError(f"Invalid Order ID ({val.id})")

        return val

    def get(self, id: int) -> Order | None:
        try:
            return self.hash_map[id]
        except KeyError:
            raise KeyError(f"Invalid Order ID ({id})")
