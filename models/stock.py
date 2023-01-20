from constants.global_contexts import kite_context

class Stock:
    stock_name:str
    exchange:str

    def __init__(
            self,
            symbol:str,
            exchange:str
        ) -> None:
        self.stock_name = symbol
        self.exchange = exchange

    @property
    def current_price(self):
        try:
            return kite_context.ltp([f"NSE:{self.stock_name}"])[f"NSE:{self.stock_name}"]["last_price"]
        except:
            return None