import requests
import json
from logging import Logger

from models.position import Position

from constants.global_contexts import kite_context
from constants.kite_credentials import API_KEY
from constants.enums.position import PositionType

from utils.logger import get_logger

logger:Logger = get_logger(__name__)

class Account:
    """
        Account contains all the details associated with the zerodha account
    """

    def __init__(
        self
        ) -> None:
        self.__available_cash:float = None
        self.positions:dict[str, Position] = {}
        self.__used_margin:float = None


    @property
    def available_cash(self)-> float:
        """
            it returns the available cash after deducting the used margin for each of the positions
        """
        if len(self.positions.keys()) > 0:
            return self.__available_cash - self.__used_margin
        return self.__available_cash

    def get_available_cash(self)->None:
        """
            fetches available live balance in the account
        """
        try:
            response = requests.get(
                url="https://api.kite.trade/user/margins",
                headers={
                        "X-Kite-Version":"3",
                        "Authorization":f"token {API_KEY}:{kite_context.access_token}",
                    }
            )
        except:
            response = None
        
        data = json.loads(response.text) if response else None
        self.__available_cash = float(data["data"]["equity"]["available"]["live_balance"]) if data else None

    
    def get_positions(self):
        """
            gets the list of all positions in the account

            here used margin is cash used along with transaction cost

            it adds up the margin used by all the positions at current stock price
            * As stock price changes transaction cost changes and hence the invested balance also changes
        """
        new_positions = kite_context.positions()

        used_margin = 0

        earlier_positions_keys = self.positions.keys()

        for position in new_positions["net"]:
            if position["tradingsymbol"] not in earlier_positions_keys:
                if position["buy_quantity"] > position["sell_quantity"]:
                    stock_position:Position = Position(
                            position_price=position["buy_price"],
                            quantity=abs(position["buy_quantity"]-position["sell_quantity"]), # the quantity can be negative
                            exchange=position["exchange"],
                            symbol=position["tradingsymbol"],
                            expected_return=self.monthly_expected_return,
                            drawdown_allowed=self.drawdown_allowed,
                            position_type=PositionType.LONG
                        )
                    if not (position["tradingsymbol"] in list(earlier_positions_keys)):
                        self.positions[position["tradingsymbol"]] = stock_position
                        logger.info(f"{position['tradingsymbol']} was bought {position['buy_quantity']}")

                    used_margin += stock_position.invested_amount
                else:

                    logger.info(f"{position['tradingsymbol']} was bought accidently. If it arises then check for bug.")

        self.__used_margin = used_margin
    
 
    def update_investment(self):
        """
            with this function, one can update the available cash, list of all positions and used margin at once
        """
        self.get_positions()
        self.get_available_cash()


    