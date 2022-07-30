from connectors.tdameritrade_broker.tdameritrade_model import TDAmeritradeModel
from interface.watchlist_component import WatchlistComponent
import logging

logger = logging.getLogger()


class WatchlistFeatureController:
    def __init__(self, model: TDAmeritradeModel, view: WatchlistComponent):
        self.model = model
        self.view = view

        self.update_watchlist_component_ui()

    def add_symbol_to_watchlist(self, symbol):
        try:
            flag = self.model.add_symbol_to_watchlist_quotes(symbol)
            if flag == 'ADDED':
                self.view.create_widgets_in_watchlist_component(symbol)
                logger.info(f'{symbol} added to the watchlist quotes data and the UI')
        except ValueError as error:
            # show an error message
            logger.error(error)

    def remove_symbol_from_watchlist(self, symbol, body_widgets_index):
        try:
            flag = self.model.remove_symbol_from_watchlist_quotes(symbol)
            if flag == 'REMOVED':
                self.view.destroy_widgets_in_watchlist_component(body_widgets_index)
                logger.info(f'{symbol} removed from the watchlist quotes data and the UI')
        except ValueError as error:
            # show an error message
            logger.error(error)


    def update_watchlist_component_ui(self):
        self.view.update_ui_widgets_with_new_data(self.model.watchlist_quotes)



