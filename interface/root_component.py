import tkinter as tk
from tkinter import ttk

from connectors.tdameritrade_broker.tdameritrade_model import TDAmeritradeModel
from interface.watchlist_component import WatchlistComponent
from controllers.watchlist_feature_controller import WatchlistFeatureController
from interface.manual_trading_component import ManualTradingComponent

from controllers.manual_trading_feature_controller import ManualTradingFeatureController


class RootComponent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Stock Trading Bot')
        #self.geometry("1920x1080")
        self.resizable(True, True)
        self.configure(background='gray')

        # configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Left first row component
        tdameritrade_model = TDAmeritradeModel()

        watchlist_component = WatchlistComponent(self)
        watchlist_component.grid(column=0, row=0)
        watchlist_feature_controller = WatchlistFeatureController(model=tdameritrade_model, view=watchlist_component)
        watchlist_component.set_controller(watchlist_feature_controller)

        manual_trading_component = ManualTradingComponent(self)
        manual_trading_component.grid(column=1, row=0)
        manual_trading_feature_controller = ManualTradingFeatureController(tdameritrade_model, manual_trading_component)
        manual_trading_component.set_controller(manual_trading_feature_controller)








        # self.right_1st_row_frame = ttk.Frame(self, height='540', width='640')
        # self.right_1st_row_frame['borderwidth'] = 5
        # self.right_1st_row_frame['relief'] = 'raised'
        # self.right_1st_row_frame.grid(column=2, row=0)
        #
        # self.left_2nd_row_frame = ttk.Frame(self, height='540', width='640')
        # self.left_2nd_row_frame['borderwidth'] = 5
        # self.left_2nd_row_frame['relief'] = 'raised'
        # self.left_2nd_row_frame.grid(column=0, row=1)
        #
        # self.middle_2nd_row_frame = ttk.Frame(self, height='540', width='640')
        # self.middle_2nd_row_frame['borderwidth'] = 5
        # self.middle_2nd_row_frame['relief'] = 'raised'
        # self.middle_2nd_row_frame.grid(column=1, row=1)
        #
        # self.right_2nd_row_frame = ttk.Frame(self, height='540', width='640')
        # self.right_2nd_row_frame['borderwidth'] = 5
        # self.right_2nd_row_frame['relief'] = 'raised'
        # self.right_2nd_row_frame.grid(column=2, row=1)





