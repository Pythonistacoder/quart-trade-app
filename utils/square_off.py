from constants.global_contexts import kite_context

from utils.take_position import short, long

def sqaure_off():
    """
        This square off any position which is open
        1. for short position with negative quantities it buys
        2. for long positions with positive quantities it sells
    """
    positions_data = kite_context.positions()["net"]

    for position in positions_data:
        if position["quantity"] != 0:
            if position["quantity"] < 0:
                long(position["tradingsymbol"],abs( position["quantity"]))
            elif position["quantity"] > 0:
                short(position["tradingsymbol"],abs( position["quantity"]))

                
