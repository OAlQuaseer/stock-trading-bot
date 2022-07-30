import tkinter
from tkinter import ttk
from interface.styles import *

from models import QuoteResponse

import logging
logger = logging.getLogger()


class WatchlistComponent(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)

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

    def set_controller(self, controller):
        self.controller = controller

    def update_ui_widgets_with_new_data(self, watchlist_quotes: dict):
        self.lower_frame.update_ui_widgets_with_new_data(watchlist_quotes)

    def add_symbol_to_watchlist(self, symbol):
        self.controller.add_symbol_to_watchlist(symbol)

    # As of now the source is hardcoded, TODO... need to change it once I have the polygon source implemented
    def create_widgets_in_watchlist_component(self, symbol):
        self.lower_frame.create_widgets_for_new_symbol_in_watchlist_table(symbol, source='TDAmeritrade')

    def remove_symbol_from_watchlist(self, symbol, body_widgets_index):
        self.controller.remove_symbol_from_watchlist(symbol, body_widgets_index)

    def destroy_widgets_in_watchlist_component(self, row_index):
        self.lower_frame.destroy_widgets_in_watchlist_component(row_index)

class _UpperFrame(ttk.Frame):
    def __init__(self, container: WatchlistComponent, **kwargs):
        super().__init__(master=container, **kwargs)
        self.container = container

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(self, text='TDAmeritrade', background=BG_COLOR,
                  foreground=FG_COLOR_2, font=BOLD_FONT).grid(row=0, column=0)

        self.tdameritrade_input_box = ttk.Entry(self, font=GLOBAL_FONT)
        self.tdameritrade_input_box.grid(row=1, column=0)
        self.tdameritrade_input_box.bind('<Return>', self._on_tdameritrade_entry_change)

        ttk.Label(self, text='Polygon', background=BG_COLOR, foreground=FG_COLOR_2,
                  font=BOLD_FONT).grid(row=0, column=1)

        self.polygon_input_box = ttk.Entry(self, font=GLOBAL_FONT)
        self.polygon_input_box.grid(row=1, column=1)
        self.polygon_input_box.bind('<Return>', self._on_polygon_entry_change)

    def _on_tdameritrade_entry_change(self, event):
        symbol: str = event.widget.get()
        if symbol is not None:
            symbol = symbol.upper()
            self.container.add_symbol_to_watchlist(symbol)
        event.widget.delete(0, tkinter.END)

    def _on_polygon_entry_change(self, event):
        symbol = event.widget.get()


class _LowerFrame(ttk.Frame):
    def __init__(self, container: WatchlistComponent, **kwargs):
        super().__init__(master=container, **kwargs)
        self.container = container
        self['padding'] = (5, 10, 5, 10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)

        self._headers = ['symbol', 'source', 'ask', 'bid', 'total vol', 'remove']
        self._body_widgets = dict()
        self._body_widgets_index = 1

        self._create_widgets()

    def _create_widgets(self):
        for index, header in enumerate(self._headers):
            ttk.Label(self, text=header.capitalize() if header != 'remove' else '', background=BG_COLOR,
                      foreground=FG_COLOR_2, font=GLOBAL_FONT).grid(row=0, column=index)

        for header in self._headers:
            self._body_widgets[header] = dict()
            if header in ['ask', 'bid']:
                self._body_widgets[header + '_var'] = dict()
            if header in ['total vol']:
                self._body_widgets['total_vol_var'] = dict()

    def create_widgets_for_new_symbol_in_watchlist_table(self, symbol: str, source: str):

        body_widgets_index = self._body_widgets_index
        body_widgets = self._body_widgets
        # TODO... need to change the widgets here to ttk widgets instead of tkinter widgets
        body_widgets['symbol'][body_widgets_index] = tkinter.Label(self, text=symbol, bg=BG_COLOR,
                                                                   fg=FG_COLOR, font=GLOBAL_FONT)
        body_widgets['symbol'][body_widgets_index].grid(row=body_widgets_index, column=0)

        body_widgets['source'][body_widgets_index] = tkinter.Label(self, text=source, bg=BG_COLOR,
                                                                   fg=FG_COLOR, font=GLOBAL_FONT)
        body_widgets['source'][body_widgets_index].grid(row=body_widgets_index, column=1)

        body_widgets['ask_var'][body_widgets_index] = tkinter.StringVar()
        body_widgets['ask'][body_widgets_index] = tkinter.Label(self,
                                                                textvariable=body_widgets['ask_var'][
                                                                    body_widgets_index]
                                                                , bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT)
        body_widgets['ask'][body_widgets_index].grid(row=body_widgets_index, column=2)

        body_widgets['bid_var'][body_widgets_index] = tkinter.StringVar()
        body_widgets['bid'][body_widgets_index] = tkinter.Label(self,
                                                                textvariable=body_widgets['bid_var'][
                                                                    body_widgets_index]
                                                                , bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT)
        body_widgets['bid'][body_widgets_index].grid(row=body_widgets_index, column=3)

        body_widgets['total_vol_var'][body_widgets_index] = tkinter.StringVar()
        body_widgets['total vol'][body_widgets_index] = tkinter.Label(self,
                                                                textvariable=body_widgets['total_vol_var'][
                                                                    body_widgets_index]
                                                                , bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT, width='10')
        body_widgets['total vol'][body_widgets_index].grid(row=body_widgets_index, column=4)



        body_widgets['remove'][body_widgets_index] = tkinter.Button(self, text='X', bg='darkred',
                                                                    fg=FG_COLOR, font=GLOBAL_FONT,
                                                                    command=lambda: self._remove_button_clicked(
                                                                        symbol,body_widgets_index))

        body_widgets['remove'][body_widgets_index].grid(row=body_widgets_index, column=5)

        self._body_widgets_index = body_widgets_index + 1

    def _remove_button_clicked(self, symbol, body_widgets_index):
        self.container.remove_symbol_from_watchlist(symbol, body_widgets_index)

    def destroy_widgets_in_watchlist_component(self, body_widgets_index):
        for key in self._body_widgets.keys():
            if type(self._body_widgets[key][body_widgets_index]) is not tkinter.StringVar:
                self._body_widgets[key][body_widgets_index].destroy()
            del self._body_widgets[key][body_widgets_index]

    def update_ui_widgets_with_new_data(self, watchlist_quotes: dict):
        try:
            for key, value in self._body_widgets['symbol'].items():
                symbol = value.cget('text')
                source = self._body_widgets['source'][key].cget('text')
                quote: QuoteResponse = watchlist_quotes[symbol]
                if source == 'TDAmeritrade':
                    if quote.bid_price is not None:
                        self._body_widgets['bid_var'][key].set(quote.bid_price)
                    if quote.ask_price is not None:
                        self._body_widgets['ask_var'][key].set(quote.ask_price)
                    if quote.total_volume is not None:
                        self._body_widgets['total_vol_var'][key].set(f"{quote.total_volume:,}")
                elif source == 'Polygon':
                    continue
                else:
                    continue

        except RuntimeError as e:
            logger.error("Error while updating the UI widgets in the watch list table with new data: %s", e)
        self.after(500, self.update_ui_widgets_with_new_data, watchlist_quotes)




