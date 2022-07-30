from interface.root_component import RootComponent
import logging
import datetime


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# to show the logs on the console we need to initialize and configure a stream handler
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# to print the logs on a file we need to initialize and configure a file handler
date_in_str = str(datetime.datetime.now().date())
file_handler = logging.FileHandler(f'./logs/{date_in_str}.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if __name__ == '__main__':
    logger.info('_____main_____')
    root = RootComponent()
    root.mainloop()


