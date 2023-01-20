class IntradayTransactionCost():
    """
        This class provides the details of all the transaction cost  of intraday or MIS transaction charged by zerodha.

        It requires buying price, selling price and quantity.

        For equity trading it is useful to set selling_price to 0 while buying and buying to 0 while selling.
        This helps us to associate cost with every tansaction.
        It seems that cost(buying, 0) +cost(0, selling) = cost(buying, selling)

        To get cost use total_tax and charges and to get profit use net_pl
    """
    brokerage_charges: float
    profit_or_loss: float
    turnover: float
    stt_total: float
    net_transaction_charges: float
    clearing_charges: float
    stamp_duty: float
    sebi_charges: float
    gst: float
    total_tax_and_charges:float
    net_pl: float

    def __init__(
        self,
        buying_price:float,
        selling_price:float,
        quantity:int,
        *args,
        **kwargs
        ) -> None:
        self.buying_price = buying_price
        self.selling_price = selling_price
        self.quantity = quantity

        # setting the common variables
        self.profit_or_loss = (self.selling_price - self.buying_price)*self.quantity
        self.turnover = (self.buying_price + self.selling_price)*self.quantity

        self.equity_charges()

    def equity_charges(self):
        """
            Calculates each and every charges associated with the stock
        """
        self.brokerage_charges = self.turnover*(0.03/100) if self.turnover*(0.03/100) < 40 else 40
        self.stt_total = (0.025/100)*self.selling_price
        self.net_transaction_charges = round((0.00345/100)*self.turnover,2)
        self.clearing_charges = 0
        self.stamp_duty = round((300/10000000)*self.buying_price*self.quantity,2)
        self.sebi_charges = round(((self.turnover/10000000)*10)*1.18,2)
        self.gst = 0.18*(self.brokerage_charges+self.net_transaction_charges+self.sebi_charges/1.18)
        self.total_tax_and_charges = self.brokerage_charges + self.stt_total + self.net_transaction_charges + self.clearing_charges +self.stamp_duty +self.gst +self.sebi_charges
        self.net_pl = self.profit_or_loss-self.total_tax_and_charges