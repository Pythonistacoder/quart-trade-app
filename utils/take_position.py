from constants.global_contexts import kite_context

from models.stock import Stock

def short(symbol:str, quantity:int):
    """
        takes a short position in situations where it will either
        1. sell the position which has already been bought, or
        2. sell a negative quantity of stocks
    """
    response_data = None
    try:
        response_data = kite_context.place_order(
            variety=kite_context.VARIETY_REGULAR,
            order_type=kite_context.ORDER_TYPE_MARKET,
            exchange=kite_context.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite_context.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            product=kite_context.PRODUCT_MIS,
            validity=kite_context.VALIDITY_DAY
        )
        stock = Stock(symbol=symbol, exchange='NSE')
    except Exception as e:
        raise e
    return response_data

def long(symbol: str, quantity: int):
    """
        takes a long position in situations where it will either
        1. buy the position which has already been short, or
        2. buy a positive quantity of stocks
    """

    try:
        kite_context.place_order(
            variety=kite_context.VARIETY_REGULAR,
            order_type=kite_context.ORDER_TYPE_MARKET,
            exchange=kite_context.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite_context.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            product=kite_context.PRODUCT_MIS,
            validity=kite_context.VALIDITY_DAY
        )
        stock = Stock(symbol=symbol, exchange='NSE')
        return True
        
    except Exception as e:
        
        return False