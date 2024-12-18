import multiprocessing
import logging
import os
import sys
import controller
import consumer

file_handler = logging.FileHandler(filename='tmp.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)
visibility_timeout_seconds = 600
poll_delay_seconds = 20 # Polling interval
max_workers = 1

def start_serving():
    return controller.app.run(port=5050, debug=False, host='0.0.0.0')

if __name__ == '__main__':
    poller = consumer.Consumer()
    multiprocessing.set_start_method('fork')
    processConsumer = multiprocessing.Process(target=poller.create_poll_workers, args=(max_workers, poll_delay_seconds, visibility_timeout_seconds))
    logger.info("start consumer")
    processConsumer.start() # Async pollers in background; no need to wait/join. Infinite.
    serviceListener = multiprocessing.Process(target=start_serving)
    logger.info("start service listener")
    serviceListener.start()
    
    logger.info("services started")
    processConsumer.join()
    serviceListener.join()
