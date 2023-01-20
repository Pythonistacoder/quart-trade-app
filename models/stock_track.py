import os
import pandas as pd

import yfinance as yf

from constants.settings import HIGHER_PRICE, LOWER_PRICE

class TrackAccount:

    def __init__(self) -> None:
        self.starting_stock_dict = self.starting_stocks()

    def starting_stocks(self):
        monthly_data:pd.DataFrame = yf.download(tickers = [f"{stock}.NS"for stock in self.load_stocks_from_csv()], period='1wk', interval ='1d',show_errors=False)
        monthly_data = monthly_data.bfill(axis='columns').dropna()
        monthly_data.to_csv("verification.csv")
        condition1 = monthly_data["Close"].iloc[-2] < HIGHER_PRICE
        condition2 = monthly_data["Close"].iloc[-2] > LOWER_PRICE
        selected_monthly_data = monthly_data["Close"][list(monthly_data["Close"].iloc[-2][condition2 & condition1].index)]
        returns = selected_monthly_data.pct_change()+1
        selected_monthly_data.iloc[-2][(returns.iloc[-2] > 1.02) & (returns.iloc[-3]>1.02)].to_csv("starting_stocks.csv")
        return dict(selected_monthly_data.iloc[-2][(returns.iloc[-2] > 1.02) & (returns.iloc[-3]>1.02)])

    @staticmethod
    def load_stocks_from_csv() -> list:
        """
            Given a file, it lists all the stocks from that file
        """
        file_path = os.getcwd() + "/EQUITY_NSE.csv" # file containing the list of all the stocks which are intended to be tracked
        stocks_from_csv = pd.read_csv(file_path, header=0)
        column_name = "Symbol"
        return list(stocks_from_csv[column_name])