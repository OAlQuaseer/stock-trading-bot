import tkinter
import tkinter as tk
from tkinter import ttk
from interface.styles import *


class ManualTradingComponent(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)

        self['borderwidth'] = 5
        self['relief'] = 'solid'

        # Upper frame structure
        self.upper_frame = _UpperFrame(self)
        self.upper_frame.grid(row=0, column=0)

        # Lower frame structure
        self.lower_frame = _LowerFrame(self)
        self.lower_frame.grid(row=1, column=0)

        # set the controller
        self.controller = None

    def add_stock_to_trade(self):
        self.controller.add_stock_to_trade()

    def set_controller(self, controller):
        self.controller = controller

    def activate_manual_trading_strategy(self, user_inputs):
        self.controller.activate_manual_trading_strategy(user_inputs)



class _UpperFrame(ttk.Frame):
    def __init__(self, container: ManualTradingComponent, **kwargs):
        super().__init__(master=container, **kwargs)
        self.container = container

        self.columnconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(self, text='Manual Trading Strategy', background=BG_COLOR,
                  foreground=FG_COLOR_2, font=BOLD_FONT).grid(row=0, column=0)

        self.tdameritrade_input_box = ttk.Button(self, text="Add Stock to Trade",
                                                 command=self._add_stock_button_clicked)
        self.tdameritrade_input_box.grid(row=1, column=0)

    def _add_stock_button_clicked(self):
        self.container.add_stock_to_trade()


class _LowerFrame(ttk.Frame):
    def __init__(self, container: ManualTradingComponent, **kwargs):
        super().__init__(master=container, **kwargs)
        self.container = container
        self['padding'] = (5, 10, 5, 10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)

        self._headers = ['symbol', 'balance', 'qty', 'ltp', 'ep', 'sl', 'pt', 'activate', 'remove']
        self._body_widgets = dict()
        self._body_widgets_index = 1

        self._create_label_widgets()

    def _create_label_widgets(self):
        for index, header in enumerate(self._headers):
            ttk.Label(self, text=header.capitalize() if header != 'remove' else '', background=BG_COLOR,
                      foreground=FG_COLOR_2, font=GLOBAL_FONT).grid(row=0, column=index)

        for header in self._headers:
            self._body_widgets[header] = dict()
            if header not in ['activate', 'remove']:
                self._body_widgets[header + '_var'] = dict()

    def create_widgets_for_stock_trading_inputs(self, symbols_to_trade: list):

        body_widgets_index = self._body_widgets_index
        body_widgets = self._body_widgets

        body_widgets['symbol_var'][body_widgets_index] = tkinter.StringVar(self)
        body_widgets['symbol'][body_widgets_index] = ttk.OptionMenu(self, body_widgets['symbol_var'][body_widgets_index]
                                                                    , '', *symbols_to_trade)
        body_widgets['symbol'][body_widgets_index].grid(row=body_widgets_index, column=0)

        body_widgets['balance_var'][body_widgets_index] = tkinter.StringVar(self)
        body_widgets['balance'][body_widgets_index] = ttk.Entry(self, font=GLOBAL_FONT, width=8)
        body_widgets['balance'][body_widgets_index].grid(row=body_widgets_index, column=1)
        body_widgets['balance'][body_widgets_index].bind('<Return>',
                                                         lambda event: body_widgets['balance_var'][body_widgets_index]
                                                         .set(event.widget.get()))

        body_widgets['qty_var'][body_widgets_index] = tkinter.StringVar(self)
        body_widgets['qty'][body_widgets_index] = ttk.Entry(self, font=GLOBAL_FONT, width=8)
        body_widgets['qty'][body_widgets_index].grid(row=body_widgets_index, column=2)
        body_widgets['qty'][body_widgets_index].bind('<Return>',
                                                     lambda event: body_widgets['qty_var'][body_widgets_index]
                                                     .set(event.widget.get()))

        body_widgets['ltp_var'][body_widgets_index] = tkinter.StringVar(self, value='False')
        body_widgets['ltp'][body_widgets_index] = ttk.Checkbutton(self, onvalue='True', offvalue='False',
                                                                  variable=body_widgets['ltp_var'][body_widgets_index])
        body_widgets['ltp'][body_widgets_index].grid(row=body_widgets_index, column=3)

        body_widgets['ep_var'][body_widgets_index] = tkinter.StringVar(self)
        body_widgets['ep'][body_widgets_index] = ttk.Entry(self, font=GLOBAL_FONT, width=8)
        body_widgets['ep'][body_widgets_index].grid(row=body_widgets_index, column=4)
        body_widgets['ep'][body_widgets_index].bind('<Return>', lambda event: body_widgets['ep_var'][body_widgets_index]
                                                    .set(event.widget.get()))

        body_widgets['sl_var'][body_widgets_index] = tkinter.StringVar(self)
        body_widgets['sl'][body_widgets_index] = ttk.Entry(self, font=GLOBAL_FONT, width=8)
        body_widgets['sl'][body_widgets_index].grid(row=body_widgets_index, column=5)
        body_widgets['sl'][body_widgets_index].bind('<Return>',
                                                    lambda event: body_widgets['sl_var'][body_widgets_index]
                                                    .set(event.widget.get()))

        body_widgets['pt_var'][body_widgets_index] = tkinter.StringVar(self)
        body_widgets['pt'][body_widgets_index] = ttk.Entry(self, font=GLOBAL_FONT, width=8)
        body_widgets['pt'][body_widgets_index].grid(row=body_widgets_index, column=6)
        body_widgets['pt'][body_widgets_index].bind('<Return>',
                                                    lambda event: body_widgets['pt_var'][body_widgets_index]
                                                    .set(event.widget.get()))

        body_widgets['activate'][body_widgets_index] = ttk.Button(self, width=16, text="Place Order",
                                                                  command=lambda: self._place_order_button_clicked(body_widgets_index))
        body_widgets['activate'][body_widgets_index].grid(row=body_widgets_index, column=7)

        body_widgets['remove'][body_widgets_index] = tkinter.Button(self, text='X', bg='darkred',
                                                                    fg=FG_COLOR, font=GLOBAL_FONT,
                                                                    command=lambda:
                                                                    self._remove_trade_record_from_table(body_widgets_index))
        body_widgets['remove'][body_widgets_index].grid(row=body_widgets_index, column=8)

        self._body_widgets_index = body_widgets_index + 1

    def _place_order_button_clicked(self, body_widgets_index):
        print(self._body_widgets['symbol_var'][body_widgets_index].get())
        print(self._body_widgets['balance_var'][body_widgets_index].get())
        print(self._body_widgets['qty_var'][body_widgets_index].get())
        print(self._body_widgets['ltp_var'][body_widgets_index].get())
        print(self._body_widgets['ep_var'][body_widgets_index].get())
        print(self._body_widgets['sl_var'][body_widgets_index].get())
        print(self._body_widgets['pt_var'][body_widgets_index].get())

        # TODO... need to convert it into a strategy class
        user_inputs = {
            'symbol': self._body_widgets['symbol_var'][body_widgets_index].get(),
            'balance': float(self._body_widgets['balance_var'][body_widgets_index].get()),
            'quantity': int(self._body_widgets['qty_var'][body_widgets_index].get()),
            'last_traded_price_flag': True if self._body_widgets['ltp_var'][body_widgets_index].get() == 'True' else False,
            'entry_point': float(self._body_widgets['ep_var'][body_widgets_index].get()),
            'stop_loss': float(self._body_widgets['sl_var'][body_widgets_index].get()),
            'profit_target': float(self._body_widgets['pt_var'][body_widgets_index].get()),
        }
        self.container.activate_manual_trading_strategy(user_inputs)

    def _remove_trade_record_from_table(self, body_widgets_index):
        pass

