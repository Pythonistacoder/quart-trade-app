from models.intraday_trading_cost import IntradayTransactionCost

from constants.enums.position import PositionType

def maximum_quantity(maximum_investment:float, current_price:int, position_type:PositionType)->int:
    """
        maximum quantity which can be bought so that it remains within the investment level
    """
    quantity:int = int(maximum_investment/current_price)
    if quantity>0:
        current_investment:float = breakeven_transaction_cost(current_price, quantity, position_type) + current_price*quantity
        while(current_investment>maximum_investment):
            quantity -=1
            current_investment = breakeven_transaction_cost(current_price, quantity, position_type) + current_price*quantity
    return quantity
    
def breakeven_transaction_cost(current_price:float, quantity:int, position_type:PositionType)->float:
    """
        minimum transaction cost to bear to enconter breakeven for both short and long position
    """

    buying_price:float = None
    selling_price:float = None

    if position_type == PositionType.LONG:
        buying_price = current_price
    else:
        selling_price = current_price

    steps = current_price/1000
    counter = steps
    results = []
    cost_list = []
    while (counter <= steps*200):
        if position_type == PositionType.LONG:
            selling_price = buying_price + counter
        else:
            buying_price = selling_price - counter

        cost = IntradayTransactionCost(
            buying_price=buying_price,
            selling_price=selling_price,
            quantity=quantity
        ).total_tax_and_charges

        cost_list.append(cost)
        results.append(abs(buying_price + cost - selling_price))
        counter += steps
    return cost_list[results.index(min(results))]