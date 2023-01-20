from datetime import datetime
from asyncio import sleep
from logging import Logger

import schedule

from models.stock import Stock
from models.account import Account
from models.stock_track import TrackAccount

from constants.enums.position import PositionType

from utils.take_position import long
from utils.square_off import sqaure_off

from service.computation_services import maximum_quantity

from utils.logger import get_logger

logger:Logger = get_logger(__name__)

account: Account = Account()
track_account: TrackAccount = None
stocks_to_invest:dict = None

def stock_selection_job():
    global stocks_to_invest
    track_account: TrackAccount = TrackAccount()
    stocks_to_invest = track_account.starting_stock_dict

def main_trading():
    global stocks_to_invest, logger
    if stocks_to_invest is None:
        return
    investment_list = []
    for stock_str in stocks_to_invest.keys():
        account.get_positions() 
        stock_st = stock_str[:-3]
        available_cash = account.available_cash
        if available_cash:
            if  available_cash > 500:
                individual_allocation = 300
                stock = Stock(symbol=stock_st, exchange="NSE")
                stock_price = stock.current_price
                if stock_price and stock_price<(stocks_to_invest[stock_str]*1.01):
                    quantity = maximum_quantity(individual_allocation, stock_price, PositionType.LONG)
                    if quantity > 0:
                        try:
                            long(symbol=stock.stock_name,quantity=quantity)
                            logger.info(f"{stock_st} was bought at {stock_price}")
                            investment_list.append(stock_str)
                        except:
                            continue
    for stock_name in investment_list:
        try:
            del stocks_to_invest[stock_name]
        except:
            continue
    
    #changing position logic
    stocks_to_delete = []
    for position in account.positions.values():
        if position.breached():
            logger.info(f"buy {position.stock.stock_name}")
            stocks_to_delete.append(position.stock.stock_name)
    for stock_del in stocks_to_delete:
        del account.positions[stock_del]
    

async def background_task():
    """
        all the tasks mentioned here will be running in the background
    """
    global account, stocks_to_invest, logger

    logger.info("BACKGROUND TASK STARTED")

    account.update_investment()

    try:
        schedule.every().day.at("09:12").do(stock_selection_job)
        schedule.every(5).seconds.until("15:05")
    except:
        pass

    while len(stocks_to_invest) > 0:
        schedule.run_pending()
        await sleep(1)
        current_time = datetime.now()
        if current_time.hour >= 15 and current_time.min >= 5:
            break

    # section clears out all the positions after the loops end at end_time
    sqaure_off()

    logger.info("TASK ENDED")

    
