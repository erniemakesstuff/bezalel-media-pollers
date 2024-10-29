import multiprocessing
import logging
import sys
import health_service
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
app = health_service.app # Flask run initializes server.

if __name__ ==  '__main__':
    logger.info("creating processes")
    processConsumer = multiprocessing.Process(target=consumer.start_poll)
    logger.info("start consumer")
    processConsumer.start() # Async pollers in background; no need to wait/join. Infinite.

    serviceListener = multiprocessing.Process(target=app.run(port=5050, debug=True, host='0.0.0.0'))
    logger.info("start service listener")
    serviceListener.start()

    logger.info("services started")
    processConsumer.join()
    serviceListener.join()
