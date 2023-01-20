from models.stock import Stock
from logging import Logger

from constants.enums.position import PositionType

from models.intraday_trading_cost import IntradayTransactionCost

from utils.take_position import short, long

from utils.logger import get_logger

logger:Logger = get_logger(__name__)

class Position:
    """
        object is created whenever a stock is bought either in MIS or CNC.

        For this position, intraday cost is used.

        It takes
            - _id: ObjectId() is the id saved in the database
            - buying_price: price at which the stock is bought
            - quantity: quantity bought
            - exchange: stock echange
            - symbol: symbol of the stock 
            - monthly_allowed_return: monthly return in 0.0x format 
    """

    def __init__(
        self,
        position_price:float = None,
        quantity:int = 1,
        exchange:str = "NSE",
        symbol:str = None,
        position_type:PositionType = PositionType.SHORT,
        *args,
        **kwargs
        ) -> None:
        self.position_price: float = position_price
        self.holding_quantity: int = quantity
        self.position_type:PositionType = position_type
        self.stock: Stock = Stock(symbol=symbol, exchange=exchange)
        self.last_price = self.stock.current_price
        
        # attributes which are internally used in the object
        self.__trigger = None

    @property
    def invested_amount(self) -> float:
        """
            amount invested in this stock (transaction cost is not included)
        """
        return self.position_price * abs(self.holding_quantity)

    def transaction_cost(self, buying_price, selling_price)->float:
        return IntradayTransactionCost(
            buying_price=buying_price,
            selling_price=selling_price,
            quantity=self.holding_quantity
        ).total_tax_and_charges

    @property
    def trigger(self)->float:
        return self.__trigger

    def set_trigger(self, stock_price:float):

        cost = None
        selling_price:float = None
        buy_price:float = None

        if self.position_type == PositionType.LONG:
            buy_price = self.position_price
        else:
            buy_price = stock_price

        if self.position_type == PositionType.LONG:
            selling_price = stock_price
        else:
            selling_price = self.position_price

        tx_cost = self.transaction_cost(
                buying_price=buy_price,
                selling_price=selling_price
            )/self.holding_quantity

        cost = buy_price+tx_cost
            
        initial_return = 0.01 if self.position_type == PositionType.SHORT else 0.01
        incremental_return = 0.005 if self.position_type == PositionType.SHORT else 0.005

        counter = 0

        while cost*(1 + initial_return + counter*incremental_return) < selling_price:
            if self.position_type == PositionType.SHORT:
                self.__trigger = selling_price/(1 + initial_return + counter*incremental_return)
            else:
                self.__trigger = cost*(1 + initial_return + counter*incremental_return)
            counter += 1

        drawdown:float = 1.025 if self.position_type == PositionType.LONG else 1.02

        if selling_price*drawdown <= cost:
            self.__trigger = selling_price*drawdown

    def breached(self):
        """
            if current price is less than previous trigger then it sells else it updates the trigger
        """
        global logger

        latest_price = self.stock.current_price
        if latest_price:
            self.last_price = latest_price

        if self.position_type == PositionType.LONG:
            logger.info(f"{self.stock.stock_name} Earlier trigger:  {self.__trigger}, last price:{self.last_price}")
            if self.trigger:
                if self.last_price < self.__trigger:
                    short(symbol=self.stock.stock_name,quantity=self.holding_quantity)
                    logger.info(f"Selling {self.stock.stock_name} at {self.last_price} Quantity:{self.holding_quantity}")
                    return True
            self.set_trigger(self.last_price)
            return False
        else:
            logger.info(f"{self.stock.stock_name} Earlier trigger:  {self.__trigger}, last price:{self.last_price}")
            if self.trigger:
                if self.last_price > self.__trigger:
                    logger.info(f"Buying {self.stock.stock_name} at {self.last_price} Quantity:{self.holding_quantity}")
                    long(symbol=self.stock.stock_name,quantity=self.holding_quantity)
                    return True
            self.set_trigger(self.last_price)
            return False
